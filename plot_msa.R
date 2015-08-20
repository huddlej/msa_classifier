library(ggplot2)

cbPalette <- c("#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

args <- commandArgs(trailingOnly=TRUE)
input.file <- args[1]
plot.file <- args[2]

data <- read.table(input.file, header=TRUE, sep="\t")

pdf(plot.file, width=8, height=2)
ggplot() + geom_linerange(data=data, aes(x=position, ymin=-1, ymax=1, colour=factor(bases)), alpha=0.7) + theme_bw() + theme(axis.text.y = element_blank(), axis.ticks.y = element_blank()) + scale_colour_manual(values=cbPalette)
dev.off()
