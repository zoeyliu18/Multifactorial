library(brms)
library(lme4)
library(data.table)
library(wesanderson)
library(tidyverse)

prior=prior(student_t(3,0,10), class = b)

#### Load data for each language ####

data <- read.csv('Czech_regression.csv', header = T, sep = ',')
#data <- subset(data, Semantic_closeness != 'NONE')

unique(data$Position)

data$Len <- scale(data$Len,center=TRUE,scale=TRUE)
data$Semantic_closeness <- scale(data$Semantic_closeness,center=TRUE,scale=TRUE)
data$Lexical_frequency <- scale(data$Lexical_frequency,center=TRUE,scale=TRUE)
data$Predictability <- scale(data$Predictability,center=TRUE,scale=TRUE)

pre <- subset(data, Position == 'Preverbal')
post <- subset(data, Position == 'Postverbal')

nrow(pre)
nrow(post)

###### Bayesian Models ######

pre_m <- brm(Order ~ Len + Semantic_closeness + Lexical_frequency + Pronominality +  Predictability #+ Pronominality 
             + (1|Verb),
             data = pre,
             warmup = 200,
             iter = 2000,
             chains = 20,
             #               inits="random",
             inits = "0",
             prior = prior,
             family = 'bernoulli',
             control = list(adapt_delta = 0.99, max_treedepth = 15),
             cores = 4) #,
#      file = "sk_post")

fixed_pre <-data.frame(summary(pre_m)$fixed)
names(fixed_pre) <- c('Mean', 'SE', 'CI25', 'CI975', 'Rhat', 'Bulk_ESS', 'Tail_ESS')
fixed_pre$Factor <- rownames(fixed_pre)
fixed_pre$Order <- rep('Czech preverbal', nrow(fixed_pre))
write.csv(fixed_pre,"cs_pre.csv",row.names=TRUE)


post_m <- brm(Order ~ Len + Semantic_closeness + Lexical_frequency  +  Predictability + Pronominality 
             + (1|Verb),
             data = post,
             warmup = 200,
             iter = 2000,
             chains = 20,
             inits = "0",
             prior = prior,
             family = 'bernoulli',
             control = list(adapt_delta = 0.99, max_treedepth = 15),
             cores = 4) 

fixed_post <-data.frame(summary(post_m)$fixed)
names(fixed_post) <- c('Mean', 'SE', 'CI25', 'CI975', 'Rhat', 'Bulk_ESS', 'Tail_ESS')
fixed_post$Factor <- rownames(fixed_post)
fixed_post$Order <- rep('Indonesian postverbal', nrow(fixed_post))
write.csv(fixed_post,"id_post.csv",row.names=TRUE)


######### Plotting regression coeff ########

pre_regression <- subset(read.csv('pre.csv', header = T, sep = ','), Factor != 'Intercept' & Factor != 'Pronominality')
post_regression <- subset(read.csv('post.csv', header = T, sep = ','), Factor != 'Intercept' & Factor != 'Pronominality')
both_regression <- subset(read.csv('both.csv', header = T, sep = ','), Factor != 'Intercept' & Factor != 'Pronominality')

pre_regression$Mean <- as.numeric(pre_regression$Mean)
pre_regression$CI25 <- as.numeric(pre_regression$CI25)
pre_regression$CI975 <- as.numeric(pre_regression$CI975)
post_regression$Mean <- as.numeric(post_regression$Mean)
post_regression$CI25 <- as.numeric(post_regression$CI25)
post_regression$CI975 <- as.numeric(post_regression$CI975)
both_regression$Mean <- as.numeric(both_regression$Mean)
both_regression$CI25 <- as.numeric(both_regression$CI25)
both_regression$CI975 <- as.numeric(both_regression$CI975)

for (i in 1:nrow(pre_regression)) {
  if (as.vector(pre_regression$Factor)[i] == 'Len') {
    pre_regression$Factor[i] = 'Dependency length'
  }
  
  if (as.vector(pre_regression$Factor)[i] == 'Lexical_frequency') {
    pre_regression$Mean[i] = pre_regression$Mean[i] * (-1)
    pre_regression$CI25[i] = pre_regression$CI25[i] * (-1)
    pre_regression$CI975[i] = pre_regression$CI975[i] * (-1)
    pre_regression$Factor[i] = 'Lexical frequency'
  }
  
  if (as.vector(pre_regression$Factor)[i] == 'Semantic_closeness') {
    pre_regression$Factor[i] = 'Semantic closeness'
  }
}

for (i in 1:nrow(post_regression)) {
  if (as.vector(post_regression$Factor)[i] == 'Len') {
    post_regression$Factor[i] = 'Dependency length'
  }
  
  if (as.vector(post_regression$Factor)[i] == 'Lexical_frequency') {
    post_regression$Mean[i] = post_regression$Mean[i] * (-1)
    post_regression$CI25[i] = post_regression$CI25[i] * (-1)
    post_regression$CI975[i] = post_regression$CI975[i] * (-1)
    post_regression$Factor[i] = 'Lexical frequency'
  }
  
  if (as.vector(post_regression$Factor)[i] == 'Semantic_closeness') {
    post_regression$Factor[i] = 'Semantic closeness'
  }
}

for (i in 1:nrow(both_regression)) {
  if (as.vector(both_regression$Factor)[i] == 'Len') {
    both_regression$Factor[i] = 'Dependency length'
  }
  
  if (as.vector(both_regression$Factor)[i] == 'Lexical_frequency') {
    both_regression$Mean[i] = both_regression$Mean[i] * (-1)
    both_regression$CI25[i] = both_regression$CI25[i] * (-1)
    both_regression$CI975[i] = both_regression$CI975[i] * (-1)
    both_regression$Factor[i] = 'Lexical frequency'
  }
  
  if (as.vector(both_regression$Factor)[i] == 'Semantic_closeness') {
    both_regression$Factor[i] = 'Semantic closeness'
  }
}


pre_regression$Factor <- factor(pre_regression$Factor,levels=c('Dependency length', 'Semantic closeness', 'Lexical frequency', 'Predictability')) #, 'Pronominality')) 
post_regression$Factor <- factor(post_regression$Factor,levels=c('Dependency length', 'Semantic closeness', 'Lexical frequency', 'Predictability')) #, 'Pronominality')) 
both_regression$Factor <- factor(both_regression$Factor,levels=c('Dependency length', 'Semantic closeness', 'Lexical frequency', 'Predictability')) #, 'Pronominality')) 

all <- rbind(pre_regression, post_regression, both_regression)


pre_regression$Order <- factor(pre_regression$Order,levels=c('Chinese preverbal', 'Persian preverbal', 'Japanese preverbal', 'Hindi preverbal')) 
post_regression$Order <- factor(post_regression$Order, levels = c('Arabic postverbal', 'Hebrew postverbal', 'Indonesian postverbal', 'Greek postverbal', 'Swedish postverbal'))
both_regression$Order <- factor(both_regression$Order, levels = c('Spanish postverbal', 'Spanish preverbal', 'Italian postverbal', 'Italian preverbal', 'Ukrainian postverbal', 'Ukrainian preverbal', 'Russian postverbal', 'Russian preverbal', 'Czech postverbal', 'Czech preverbal', 'Polish postverbal', 'Polish preverbal', 'Bulgarian postverbal', 'Bulgarian preverbal', 'Croatian postverbal', 'Croatian preverbal', 'Dutch postverbal', 'Dutch preverbal', 'German postverbal', 'German preverbal', 'English postverbal', 'English preverbal'))

pre_regression$Significant <- factor(pre_regression$Significant,levels=c("no", "yes positive")) 
post_regression$Significant <- factor(post_regression$Significant,levels=c("no", "yes positive", "yes negative")) 
both_regression$Significant <- factor(both_regression$Significant,levels=c("no", "yes positive", "yes negative")) 


p1 <- ggplot(pre_regression, aes(x=Order,y=Mean,color=Factor)) + 
  #  geom_errorbar(aes(ymax = CI975, ymin = CI25), width=.1, position=position_dodge(.9)) +
  geom_point(size = 5, aes(shape=Significant, color=Significant)) +
  labs(y="Coefficient") +
  scale_color_manual(values=c("steelblue", "#D16103", "#52854C", "#7570b3")) +
  coord_flip() +
  facet_wrap(~Factor,ncol=5) +
  theme_minimal(base_size = 24) +  
  #  theme_minimal(legend.position="top")+
  geom_hline(yintercept=0, linetype = "dashed") +
  theme(legend.position="none")

p1

ggsave("preverbal_coef.pdf", p1, height = 4)


p2 <- ggplot(post_regression, aes(x=Order,y=Mean,color=Factor)) + 
#  geom_errorbar(aes(ymax = CI975, ymin = CI25), width=.1, position=position_dodge(.9)) +
  geom_point(size = 5, aes(shape=Significant, color=Significant)) +
  labs(y="Coefficient") +
  scale_color_manual(values=c("steelblue", "#D16103", "#52854C", "#7570b3")) +
  coord_flip() +
  facet_wrap(~Factor,ncol=5) +
  theme_minimal(base_size = 24) +  
  #  theme_minimal(legend.position="top")+
  geom_hline(yintercept=0, linetype = "dashed") +
  theme(legend.position="none")

p2

ggsave("postverbal_coef.pdf", p2, height = 5)


p3 <- ggplot(both_regression, aes(x=Order,y=Mean,color=Factor)) + 
#  geom_errorbar(aes(ymax = CI975, ymin = CI25), width=.1, position=position_dodge(.9)) +
  #  geom_line() +
  geom_point(size = 5, aes(shape=Significant, color=Significant)) +
  labs(y="Coefficient") +
  scale_color_manual(values=c("steelblue", "#D16103", "#52854C", "#7570b3")) +
  coord_flip() +
  facet_wrap(~Factor,ncol=5) +
  theme_minimal(base_size = 24) +  
  #  theme_minimal(legend.position="top")+
  geom_hline(yintercept=0, linetype = "dashed") +
  theme(legend.position="none")

p3

ggsave("both_coef.pdf", p3, height = 12)

dl <- subset(both_regression,Factor=='Dependency length')
dl$Language <- factor(dl$Language, levels = c('English', 'German', 'Dutch', 'Croatian', 'Bulgarian', 'Polish', 'Czech', 'Russian', 'Ukrainian', 'Italian', 'Spanish'))
names(dl) <- c('Mean', 'SE', 'CI25', 'CI975', '', '', '', '', 'Factor', 'Order', 'Language', 'PP ordering domain')

p4 <- ggplot(dl, aes(x=Simple_Order,y=Mean,color=Simple_Order)) + 
  geom_point(aes(color=Simple_Order)) +
  geom_text(aes(label=paste(round(Mean,2))), vjust=-2.5,position=position_dodge(.9),size=5)+
  geom_errorbar(aes(ymin=CI25, ymax=CI975),width=.1,position=position_dodge(.9))+
  scale_color_manual(name= 'PP ordering domain', values=c("#D16103","#7570b3")) +
  labs(x="Language")+labs(y="Coefficient") +
  scale_y_continuous(limits=c(-25,11)) +
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.title.y=element_text(size=24),
        axis.text.y=element_text(size=24),
        strip.text = element_text(size=24),
        legend.title=element_text(size=24),
        legend.text=element_text(size=24)) + 
  theme(legend.position="top") +
  facet_wrap(~Language,ncol=6)
  
p4


################### Calculating prediction accuracy for larger model ###########

options (contrasts = rep("contr.sum", 2))

data <- read.csv('Hindi_regression.csv', header = T, sep = ',')

language = 'English postverbal'

data <- subset(all_data, Language == language)
rownames(data) <- 1:nrow(data)

num1 = nrow(data)
num2 = nrow(data) / 2

se <- function(x){sd(x)/sqrt(length(x))}

test_num = round(num1/10, digit=0)
train_num = num1 - test_num

#acc1 = acc2 = acc3 = acc4 = acc5 = acc6 = acc7 = rep(10,0)
acc1 = acc2 = acc3 = acc4 = acc5 = acc6 = acc7 = c()

for (i in 1:10000){
  use = sample(1:num1, test_num,replace=FALSE)
  
  a = b = c = d = e = f = g = h = i = j = k = l = 0
  
  train = data[-which(1:nrow(data) %in% use),]
  test = data[use,]
  
  mod1 = 'Dependency length'
  mod2 = glm(Order ~ Len + Semantic_closeness, data = train, family = 'binomial')
  mod3 = glm(Order ~ Len + Semantic_closeness + Lexical_frequency, data = train, family = 'binomial')
  mod4 = glm(Order ~ Len + Semantic_closeness + Lexical_frequency + Predictability, data=train, family='binomial')
#  mod5 = glm(Order ~ Len + Semantic_closeness + Lexical_frequency + Predictability + PMI, data=train, family='binomial')
  mod5 = glm(Order ~ Len + Semantic_closeness + Lexical_frequency + Predictability + Pronominality, data=train, family='binomial')
  mod6 = glmer(Order ~ Len + Semantic_closeness + Lexical_frequency + Predictability + Pronominality + (1 | Verb), data=train, family='binomial', control=glmerControl(optimizer="bobyqa"))
  
  
  row = data.frame(as.numeric(row.names(test)))
  
  ###########
  
  pred1 = nrow(subset(test, Len == 1)) / test_num
  #  print(typeof(pred1))
  #  acc1[i] = pred1
  acc1 = c(acc1, pred1)
  
  ########### 
  
  pred2 = data.frame(predict(mod2,test,type="response"))
  oppo2 = 1 - pred2
  
  for (m in 1:nrow(pred2)){
    if (row[m,] <= num2){
      if (pred2[m,] > oppo2[m,]){
        a = a + 1}}
    if (row[m,] > num2){
      if (pred2[m,] < oppo2[m,]){
        b = b + 1}}
  }
  
  #  acc2[i] = (a+b) / test_num
  acc2 = c(acc2, (a+b) / test_num)
  
  ############
  
  pred3 = data.frame(predict(mod3,test,type="response"))
  oppo3 = 1 - pred3
  
  for (m in 1:nrow(pred3)){
    if (row[m,] <= num2){
      if (pred3[m,] > oppo3[m,]){
        c = c + 1}}
    if (row[m,] > num2){
      if (pred3[m,] < oppo3[m,]){
        d = d + 1}}
  }
  
  #  acc3[i] = (c+d) / test_num
  acc3 = c(acc3, (c+d) / test_num)
  
  ###########
  
  pred4 = data.frame(predict(mod4,test,type="response"))
  oppo4 = 1 - pred4
  
  for (m in 1:nrow(pred4)){
    if (row[m,] <= num2){
      if (pred4[m,] > oppo4[m,]){
        e = e + 1}}
    if (row[m,] > num2){
      if (pred4[m,] < oppo4[m,]){
        f = f + 1}}
  }
  
  #  acc4[i] = (e+f) / test_num
  acc4 = c(acc4, (e+f) / test_num)
  
  ###########
  
  pred5 = data.frame(predict(mod5,test,type="response"))
  oppo5 = 1 - pred5
  
  for (m in 1:nrow(pred5)){
    if (row[m,] <= num2){
      if (pred5[m,] > oppo5[m,]){
        g = g + 1}}
    if (row[m,] > num2){
      if (pred5[m,] < oppo5[m,]){
        h = h + 1}}
  }
  
  #  acc5[i] = (g+h) / test_num
  acc5 = c(acc5, (g+h) / test_num)
  
  ###########
  
  pred6 = data.frame(predict(mod6,test,type="response",re.form = NULL, allow.new.levels = TRUE))
  oppo6 = 1 - pred6
  
  for (m in 1:nrow(pred6)){
    if (row[m,] <= num2){
      if (pred6[m,] > oppo6[m,]){
        i = i + 1}}
    if (row[m,] > num2){
      if (pred6[m,] < oppo6[m,]){
        j = j + 1}}
  }
  
  #  acc6[i] = (i+j) / test_num
  acc6 = c(acc6, (i+j) / test_num)
  
}

acc1 = sort(acc1, decreasing=FALSE)
acc1_mean = mean(acc1)
acc1_CI250 = acc1[250]
acc1_CI9750 = acc1[9750]

acc2 = sort(acc2, decreasing=FALSE)
acc2_mean = mean(acc2)
acc2_CI250 = acc2[250]
acc2_CI9750 = acc2[9750]

acc3 = sort(acc3, decreasing=FALSE)
acc3_mean = mean(acc3)
acc3_CI250 = acc3[250]
acc3_CI9750 = acc3[9750]

acc4 = sort(acc4, decreasing=FALSE)
acc4_mean = mean(acc4)
acc4_CI250 = acc4[250]
acc4_CI9750 = acc4[9750]

acc5 = sort(acc5, decreasing=FALSE)
acc5_mean = mean(acc5)
acc5_CI250 = acc5[250]
acc5_CI9750 = acc5[9750]

acc6 = sort(acc6, decreasing=FALSE)
acc6_mean = mean(acc6)
acc6_CI250 = acc6[250]
acc6_CI9750 = acc6[9750]


output <- file("/workspace/raw_data/data/English_postverbal_acc.txt")

writeLines(c("Mod1", acc1_mean, acc1_CI250, acc1_CI9750,  
             "Mod2", acc2_mean, acc2_CI250, acc2_CI9750,
             "Mod3", acc3_mean, acc3_CI250, acc3_CI9750,
             "Mod4", acc4_mean, acc4_CI250, acc4_CI9750,
             "Mod5", acc5_mean, acc5_CI250, acc5_CI9750,
             "Mod6", acc6_mean, acc6_CI250, acc6_CI9750), output)
close(output)



########### Linear Models ###########

#### Gradient model ####

pre_m <- glmer(Order ~ Len + Semantic_closeness + Lexical_frequency  +  Predictability + Pronominality 
               + (1|Verb),
               data = pre,
               family = "binomial")

post_m <- glmer(Order ~ Len + Semantic_closeness + Lexical_frequency  +  Predictability + Pronominality 
                + (1|Verb),
                data = post,
                family = "binomial")

#### Categorical model ####

pre_m_c <- glmer(Order ~ Len_c + Semantic_closeness_c + Lexical_frequency_c  +  Predictability_c + Pronominality 
               + (1|Verb),
               data = pre,
               family = "binomial")

post_m_c <- glmer(Order ~ Len_c + Semantic_closeness_c + Lexical_frequency_c  +  Predictability_c + Pronominality 
                + (1|Verb),
                data = post,
                family = "binomial")


#### Saving coeff of gradient model ####

fixed_pre <-data.frame(summary(pre_m)$coef)
names(fixed_pre) <- c('Mean', 'SE', 'z-value', 'Pr')
fixed_pre$Factor <- rownames(fixed_pre)
fixed_pre$Order <- rep('English preverbal', nrow(fixed_pre))
write.csv(fixed_pre,"en_pre.csv",row.names=TRUE)

fixed_post <-data.frame(summary(post_m)$coef)
names(fixed_post) <- c('Mean', 'SE', 'z-value', 'Pr')
fixed_post$Factor <- rownames(fixed_post)
fixed_post$Order <- rep('English postverbal', nrow(fixed_post))
write.csv(fixed_post,"en_post.csv",row.names=TRUE)

#### Saving coeff of categorical model ####

fixed_pre_c <-data.frame(summary(pre_m_c)$coef)
names(fixed_pre_c) <- c('Mean', 'SE', 'z-value', 'Pr')
fixed_pre_c$Factor <- rownames(fixed_pre_c)
fixed_pre_c$Order <- rep('English preverbal', nrow(fixed_pre_c))
write.csv(fixed_pre_c,"en_pre_c.csv",row.names=TRUE)

fixed_post_c <-data.frame(summary(post_m_c)$coef)
names(fixed_post_c) <- c('Mean', 'SE', 'z-value', 'Pr')
fixed_post_c$Factor <- rownames(fixed_post_c)
fixed_post_c$Order <- rep('English postverbal', nrow(fixed_post_c))
write.csv(fixed_post_c,"en_post_c.csv",row.names=TRUE)



