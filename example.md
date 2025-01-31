# claudia's tree with binary layout
python treeprofiler.py --tree ../claudia_tree/concatenate_pg3_faa_ft.nw -d /home/deng/Projects/metatree_drawer/claudia_tree/annotated_concatenate_pg3_faa_ft.tsv --taxon_column GCA --taxonomic_profile --num_column GC,size --bool_column aquatic_habitat,host_associated,soil_habitat --BinaryLayout aquatic_habitat,host_associated,soil_habitat

# highlighted by 
python treeprofiler.py -t demo/p__Thermoproteota.nw -d /home/deng/Projects/metatree_drawer/metatreedrawer/demo/metadata_p__Thermoproteota_relative_random.txt --taxonomic_profile --num_column sample1,sample2,sample3,sample4,sample5 --highlighted_by 'name!=GB_GCA_000494185.1,sample1>=0.5' --port 5002

python treeprofiler.py --tree ../claudia_tree/concatenate_pg3_faa_ft.nw --metadata ../claudia_tree/annotated_concatenate_pg3_faa_ft.tsv --num_column GC,size --bool_column aquatic_habitat,host_associated,soil_habitat --counter_stat relative --BinaryLayout aquatic_habitat,host_associated,soil_habitat --highlighted_by 'soil_habitat_counter: 1>0.5' --highlighted_by 'GC_avg>55'   --port 5001 

#Taxon 
python treeprofiler.py -t demo/p__Thermoproteota.nw -d /home/deng/Projects/metatree_drawer/metatreedrawer/demo/metadata_p__Thermoproteota_relative_random.txt --taxonomic_profile --num_column sample1,sample2,sample3,sample4,sample5 --bool_column bool_type,bool_type2 --counter_stat relative --TaxonLayout name --port 5003 --HeatmapLayout [1-5] --collapsed_by 'bool_type2_counter:True>0.5'


python treeprofiler.py -t demo/p__Thermoproteota.nw -d /home/deng/Projects/metatree_drawer/metatreedrawer/demo/metadata_p__Thermoproteota_relative_random.txt --taxonomic_profile --num_column sample1,sample2,sample3,sample4,sample5 --text_column random_type --bool_column bool_type,bool_type2 --TaxonLayout name --BinaryLayout bool_type,bool_type2 --BarplotLayout sample1,sample2

#NCBI
python treeprofiler.py --tree examples/spongilla_example.nw --taxonomic_profile --annotated_tree --taxadb NCBI --taxon_delimiter . --taxa_field 0 --TaxonLayout --interactive


# progenome

python treeprofiler.py --tree examples/progenome3.nw --metadata examples/progenome3.tsv --taxon_column GCF --taxonomic_profile --num_column GC,size --bool_column aquatic_habitat,host_associated,soil_habitat --BarplotLayout GC,size --TaxonLayout --BinaryLayout aquatic_habitat,host_associated,soil_habitat --interactive --outtree examples/progenome3_annotated.nw

python treeprofiler.py --tree examples/progenome3_annotated.nw --metadata examples/progenome3.tsv --BarplotLayout GC,size --TaxonLayout --BinaryLayout aquatic_habitat,host_associated,soil_habitat --interactive
