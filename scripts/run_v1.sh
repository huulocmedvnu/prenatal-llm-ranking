#!/bin/bash
# V1 chained runner (tmux): recode -> fallback -> CDS background -> inject -> Exomiser -> LLM re-rank -> score
set -x
B=$(cd "$(dirname "$0")/.." && pwd); cd $B; P=venv/bin/python; G=${GIAB_DIR:?set GIAB_DIR}
while tmux has-session -t recode 2>/dev/null; do sleep 30; done
$P scripts/v1_fallback.py
# coding-region background (GENCODE basic CDS +/- 50 bp)
if [ ! -s $G/HG005.cds.vcf.gz ]; then
  curl -sL -o $G/gencode.gtf.gz https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.basic.annotation.gtf.gz
  zcat $G/gencode.gtf.gz | awk -F"\t" '$3=="CDS"{s=$4-51; if(s<0)s=0; print $1"\t"s"\t"$5+50}' | sort -k1,1 -k2,2n | bedtools merge -i - > $G/cds50.bed 2>/dev/null \
    || zcat $G/gencode.gtf.gz | awk -F"\t" '$3=="CDS"{s=$4-51; if(s<0)s=0; print $1"\t"s"\t"$5+50}' | sort -k1,1 -k2,2n -u > $G/cds50.bed
  bcftools view -R $G/cds50.bed $G/HG005.vcf.gz | bcftools norm -d exact -Oz -o $G/HG005.cds.vcf.gz && tabix -f -p vcf $G/HG005.cds.vcf.gz
fi
$P scripts/v1_build.py
E=$B/tools/exomiser/exomiser-cli-15.1.0
cat > $E/application.properties <<EOF
exomiser.data-directory=${EXOMISER_DATA:?set EXOMISER_DATA}
exomiser.hg38.data-version=2512
exomiser.phenotype.data-version=2512
exomiser.phenotype.data-directory=$B/tools/exomiser/data/2512_phenotype
EOF
mkdir -p $B/v1/results
# 6 JVMs in parallel; fall back to one sequential JVM for any chunk that failed (e.g. H2 file lock)
split -n l/6 -d $B/v1/batch.txt $B/v1/chunk_
for c in $B/v1/chunk_*; do (cd $E && java -Xmx12g -jar exomiser-cli-15.1.0.jar batch $c) > logs/v1_exomiser_$(basename $c).log 2>&1 & done
wait
grep -l -i -E "locked|Exception in thread|APPLICATION FAILED" logs/v1_exomiser_chunk_*.log > $B/v1/failed_chunks.txt
if [ -s $B/v1/failed_chunks.txt ]; then
  echo "parallel run had failures, rerunning missing cases sequentially"
  : > $B/v1/batch_retry.txt
  while read l; do c=$(echo "$l" | sed 's/.*--output-filename //'); ls $B/v1/results/${c}*.genes.tsv >/dev/null 2>&1 || echo "$l" >> $B/v1/batch_retry.txt; done < $B/v1/batch.txt
  (cd $E && java -Xmx24g -jar exomiser-cli-15.1.0.jar batch $B/v1/batch_retry.txt) > logs/v1_exomiser_retry.log 2>&1
fi
for m in claude-opus-5-5 claude-sonnet-5-5 claude-haiku-5-5; do $P scripts/v1_rerank.py submit $m; done
for m in opus-5-5 sonnet-5-5 haiku-5-5; do until $P scripts/claude_batch.py collect v1_rerank_$m; do sleep 120; done; done
$P scripts/v1_rerank.py score > outputs/v1_results.txt 2>&1
echo V1_DONE
