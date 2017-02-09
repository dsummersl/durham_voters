library(data.table)

his = read.csv('ncvhis32.txt', sep='\t')
vot = read.csv('ncvoter32.txt', sep='\t')

last_election <- subset(his,election_lbl=="11/08/2016")
last_election$pct_description <- as.character(last_election$pct_description)
last_election$pct_description <- gsub("^0+","",last_election$pct_description)
last_election$voted_party_cd <- as.character(last_election$voted_party_cd)
last_election$Voted <- TRUE

dt_last_election <- data.table(last_election)
dt_vot <- data.table(vot)

non_voters <- subset(dt_vot, !(voter_reg_num %in% dt_last_election$voter_reg_num) & voter_status_desc=='ACTIVE')
non_voters$precinct_desc <- as.character(non_voters$precinct_desc)
non_voters$precinct_desc <- gsub("^0+","",non_voters$precinct_desc)
non_voters$party_cd <- as.character(non_voters$party_cd)
non_voters$Voted <- FALSE

last_election$precinct_desc <- last_election$pct_description
last_election$party_cd <- last_election$voted_party_cd
all_voters <- rbind(non_voters, last_election, fill=TRUE)

dt_all_voters <- data.table(all_voters)
summary <- dt_all_voters[ ,.N,by = list(county_id,precinct_desc,party_cd,Voted)]
write.csv(summary,'county_32_all_voters.csv',row.names=F)
