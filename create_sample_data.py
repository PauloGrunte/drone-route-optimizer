# create_sample_data.py
import pandas as pd
import os

def create_sample_ceps_file():
    """Cria arquivo de exemplo com coordenadas de CEPs"""
    data = {
        'CEP': [
            '82821020', '80010010', '80020020', '80030030', '80040040',
            '80050050', '80060060', '80070070', '80080080', '80090090',
            '80100010', '80110020', '80120030', '80130040', '80140050'
        ],
        'Latitude': [
            -25.548, -25.428, -25.435, -25.442, -25.449,
            -25.456, -25.463, -25.470, -25.477, -25.484,
            -25.491, -25.498, -25.505, -25.512, -25.519
        ],
        'Longitude': [
            -49.238, -49.267, -49.275, -49.283, -49.291,
            -49.299, -49.307, -49.315, -49.323, -49.331,
            -49.339, -49.347, -49.355, -49.363, -49.371
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Criar diretório se não existir
    os.makedirs('data', exist_ok=True)
    
    # Salvar arquivo
    df.to_csv('data/ceps_coordinates.csv', index=False)
    print("Arquivo de exemplo criado: data/ceps_coordinates.csv")

if __name__ == "__main__":
    create_sample_ceps_file()