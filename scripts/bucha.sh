#!/bin/bash

# "RestauranteOsManos2017,text"
restaurants="PauloJDuarte66,Restaurante-O-Sérgio,text restaurantegirochurrasqueira,Restaurante-Giro-Churrasqueira,text profile.php?id=61558234090568,Tasquinha-do-Barbosa,image jgmatosgarfinho,Restaurante-O-Garfinho-à-Portuguesa,image profile.php?id=100063789900247,Restaurante-&-Petiscaria-Boteko,image"

echo "Running scraper..."
poetry run python bucha/scraper.py "$restaurants"
echo "Done."