if (dir.exists("Rlib")) .libPaths(c("Rlib", .libPaths()))  # run from the repository root
library(lme4)
`%||%` <- function(a, b) if (is.null(a)) b else a
d <- read.csv("outputs/mixed_long.csv")
d$method <- relevel(factor(d$method), ref = "exomiser_hiphive")
d$period <- relevel(factor(d$period), ref = "pre")
ctl <- glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))
or <- function(m, terms) { b <- fixef(m)[terms]; ci <- confint(m, parm = terms, method = "Wald"); round(cbind(OR = exp(b), exp(ci)), 2) }
cat("== Model 1: post-cutoff fetuses, method fixed, random fetus and gene\n")
m1 <- glmer(top10 ~ method + (1 | fetus) + (1 | gene), data = subset(d, period == "post"), family = binomial, control = ctl)
print(or(m1, grep("^method", names(fixef(m1)), value = TRUE)))
print(VarCorr(m1)); cat("singular:", isSingular(m1), "\n"); print(round(coef(summary(m1)), 4))
cat("== Model 2: all fetuses, method x period, random fetus and gene\n")
m2 <- glmer(top10 ~ method * period + (1 | fetus) + (1 | gene), data = d, family = binomial, control = ctl)
print(or(m2, grep("method", names(fixef(m2)), value = TRUE)))
print(VarCorr(m2)); cat("singular:", isSingular(m2), "\n"); print(round(coef(summary(m2)), 4))
