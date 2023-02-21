
for s in $(seq 0 1 9); do cp device1-230217-1726.txt dev$s-230217-2000.txt; done



for s in $(seq 0 1 29); do 
    ns=$((s+1)); 
    ss=$(printf "%02d" ${s})
    nss=$(printf "%02d" ${ns})
    for df in dev[0-9]-*${ss}.txt; do 
        pat="s#20${ss}.txt#20${nss}.txt#"
        nf=$(echo $df | sed ${pat}); 
        seed=$RANDOM
        echo "${ss} -> ${nss}: seed: ${seed}   $df -> $nf"; 
        cat $df |awk -v  seed=${seed} 'BEGIN{srand(seed)} {$4 += int(rand()*5000); print $0}' > ${nf}
        # cat $df |awk -v  seed=${seed} 'BEGIN{srand($seed)} {$4 = $4 + int(rand()*5000); print $4}'
    done; 
    echo "-----";  
done