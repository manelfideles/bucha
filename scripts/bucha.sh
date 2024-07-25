#!/bin/bash

restaurants=(
    "RestauranteOsManos2017"
    "PauloJDuarte66"
)

get_sed_pattern() {
    case "$1" in
        "RestauranteOsManos2017")
            echo '/^| Ementa do dia /,/^| Bom Apetite!/{p;/^| Bom Apetite!/q;}'
            ;;
        "PauloJDuarte66")
            echo '/Menu €8\.50/,/Bom apetite/{p;/Bom apetite/q;}'
            ;;
        # Add more cases for other restaurants
        *)
            echo "Unknown restaurant: $1" >&2
            exit 1
            ;;
    esac
}

for restaurant in "${restaurants[@]}"
do
    echo "Processing restaurant: $restaurant"
    poetry run python bucha/scraper.py "$restaurant"    
    pattern=$(get_sed_pattern "$restaurant")
    sed -n "$pattern" "logs/${restaurant}.txt" > "menus/${restaurant}.txt"
    
done
echo "Done."