from data.database import Database

sample_news = [
    {
        'titulo': 'Nova lei protege minorias religiosas',
        'texto': 'Uma nova lei foi aprovada para garantir proteção legal a comunidades religiosas vulneráveis.',
        'url': 'https://exemplo.com/noticia1',
        'fonte': 'Exemplo News',
        'pais': 'Brasil',
        'cidade': 'São Paulo',
        'religiao': 'Cristianismo',
        'classe': 0,
        'probabilidade': 0.12,
        'explicacao_lime': 'Texto positivo sem sinais de intolerância.'
    },
    {
        'titulo': 'Ataque discursivo contra comunidade religiosa local',
        'texto': 'Líderes comunitários denunciam discurso de ódio e incitação contra a religião X em evento público.',
        'url': 'https://exemplo.com/noticia2',
        'fonte': 'Voz da Cidade',
        'pais': 'Brasil',
        'cidade': 'Rio de Janeiro',
        'religiao': 'Religião X',
        'classe': 1,
        'probabilidade': 0.92,
        'explicacao_lime': 'Palavras de ódio e ataque direto a grupo religioso.'
    },
    {
        'titulo': 'Encontro inter-religioso promove diálogo',
        'texto': 'Representantes de várias religiões se reúnem para fortalecer o respeito e a convivência pacífica.',
        'url': 'https://exemplo.com/noticia3',
        'fonte': 'Informe Social',
        'pais': 'Portugal',
        'cidade': 'Lisboa',
        'religiao': 'Multirreligioso',
        'classe': 0,
        'probabilidade': 0.08,
        'explicacao_lime': 'Notícia de colaboração e respeito entre religiões.'
    }
]

if __name__ == '__main__':
    db = Database('data/monitoring.db')
    for noticia in sample_news:
        noticia_id = db.insert_noticia(noticia)
        print(f'Inserido ID {noticia_id}: {noticia["titulo"]}')
    print('Inserção de notícias de teste concluída.')
