import pandas as pd
import psycopg2
import os
from config import ADVANCED_DB_CONFIG, CSV_FILES

def create_advanced_database_and_tables():
    conn = None
    try:
        # Conexión sin especificar la base de datos para crear una nueva
        conn = psycopg2.connect(
            user=ADVANCED_DB_CONFIG['user'],
            password=ADVANCED_DB_CONFIG['password'],
            host=ADVANCED_DB_CONFIG['host'],
            dbname='postgres' # Conectar a la base de datos por defecto
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Crear la base de datos si no existe
        db_name = ADVANCED_DB_CONFIG['dbname']
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {db_name};")
            print(f"Base de datos '{db_name}' creada.")
        else:
            print(f"Base de datos '{db_name}' ya existe.")

        # Cerrar la conexión inicial
        cur.close()
        conn.close()

        # Conectar a la nueva base de datos y crear tablas
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Definición de las tablas
        table_commands = [
            """
            CREATE TABLE IF NOT EXISTS seasons (
                season_id VARCHAR(10) PRIMARY KEY,
                season_name VARCHAR(50)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS teams (
                tm_name VARCHAR(255) PRIMARY KEY,
                season_id VARCHAR(10) REFERENCES seasons(season_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS players (
                name VARCHAR(255) PRIMARY KEY,
                role VARCHAR(50),
                nat VARCHAR(50),
                height INTEGER,
                age INTEGER,
                tm_name VARCHAR(255) REFERENCES teams(tm_name),
                season_id VARCHAR(10) REFERENCES seasons(season_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS team_stats (
                id SERIAL PRIMARY KEY,
                tm_name VARCHAR(255) REFERENCES teams(tm_name),
                season_id VARCHAR(10) REFERENCES seasons(season_id),
                gp INTEGER,
                w INTEGER,
                l INTEGER,
                min FLOAT,
                pts FLOAT,
                two_ptm FLOAT,
                two_pta FLOAT,
                two_pt_pct FLOAT,
                three_ptm FLOAT,
                three_pta FLOAT,
                three_pt_pct FLOAT,
                fgm FLOAT,
                fga FLOAT,
                fg_pct FLOAT,
                ftm FLOAT,
                fta FLOAT,
                ft_pct FLOAT,
                or_rebounds FLOAT,
                dr_rebounds FLOAT,
                tr_rebounds FLOAT,
                ast FLOAT,
                tovers FLOAT,
                st FLOAT,
                blk FLOAT,
                blka FLOAT,
                pf FLOAT,
                df FLOAT,
                val FLOAT,
                plus_minus FLOAT,
                pace FLOAT,
                poss FLOAT,
                shooting_chances FLOAT,
                off_ppp FLOAT,
                def_ppp FLOAT,
                off_rtg FLOAT,
                def_rtg FLOAT,
                net_rtg FLOAT,
                efg_pct FLOAT,
                ts_pct FLOAT,
                rim_freq FLOAT,
                rim_pps FLOAT,
                paint_freq FLOAT,
                paint_pps FLOAT,
                mid_freq FLOAT,
                mid_pps FLOAT,
                c3_freq FLOAT,
                c3_pps FLOAT,
                l3_freq FLOAT,
                l3_pps FLOAT,
                ft_ratio FLOAT,
                to_pct FLOAT,
                lto_pct FLOAT,
                dto_pct FLOAT,
                ast_pct FLOAT,
                ast_pct_2p FLOAT,
                ast_pct_3p FLOAT,
                ast_pct_ft FLOAT,
                ast_ratio FLOAT,
                ast_to_ratio FLOAT,
                or_pct FLOAT,
                or_pct_after_2p FLOAT,
                or_pct_after_3p FLOAT,
                or_pct_after_ft FLOAT,
                dr_pct FLOAT,
                dr_pct_after_2p FLOAT,
                dr_pct_after_3p FLOAT,
                dr_pct_after_ft FLOAT,
                tr_pct FLOAT,
                st_pct FLOAT,
                blk_pct FLOAT,
                blk_pct_2p FLOAT,
                blk_pct_3p FLOAT,
                kills FLOAT,
                psf_freq FLOAT,
                dsf_freq FLOAT,
                sos FLOAT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS player_stats (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) REFERENCES players(name),
                tm_name VARCHAR(255) REFERENCES teams(tm_name),
                season_id VARCHAR(10) REFERENCES seasons(season_id),
                role VARCHAR(50),
                nat VARCHAR(50),
                height INTEGER,
                age INTEGER,
                gp INTEGER,
                w INTEGER,
                l INTEGER,
                w_pct FLOAT,
                min FLOAT,
                pts FLOAT,
                two_ptm FLOAT,
                two_pta FLOAT,
                two_pt_pct FLOAT,
                three_ptm FLOAT,
                three_pta FLOAT,
                three_pt_pct FLOAT,
                fgm FLOAT,
                fga FLOAT,
                fg_pct FLOAT,
                ftm FLOAT,
                fta FLOAT,
                ft_pct FLOAT,
                or_rebounds FLOAT,
                dr_rebounds FLOAT,
                tr_rebounds FLOAT,
                ast FLOAT,
                tovers FLOAT,
                st FLOAT,
                blk FLOAT,
                blka FLOAT,
                pf FLOAT,
                df FLOAT,
                val FLOAT,
                plus_minus FLOAT,
                poss FLOAT,
                usg_pct FLOAT,
                ppp FLOAT,
                off_rtg_on FLOAT,
                def_rtg_on FLOAT,
                net_rtg_on FLOAT,
                ind_off_rtg FLOAT,
                ind_def_rtg FLOAT,
                ind_net_rtg FLOAT,
                efg_pct FLOAT,
                ts_pct FLOAT,
                rim_freq FLOAT,
                rim_pps FLOAT,
                paint_freq FLOAT,
                paint_pps FLOAT,
                mid_freq FLOAT,
                mid_pps FLOAT,
                c3_freq FLOAT,
                c3_pps FLOAT,
                l3_freq FLOAT,
                l3_pps FLOAT,
                ft_ratio FLOAT,
                to_pct FLOAT,
                lto_pct FLOAT,
                dto_pct FLOAT,
                ast_pct FLOAT,
                ast_pct_2p FLOAT,
                ast_pct_3p FLOAT,
                ast_pct_ft FLOAT,
                ast_ratio FLOAT,
                ast_to_ratio FLOAT,
                or_pct FLOAT,
                or_pct_after_2p FLOAT,
                or_pct_after_3p FLOAT,
                or_pct_after_ft FLOAT,
                dr_pct FLOAT,
                dr_pct_after_2p FLOAT,
                dr_pct_after_3p FLOAT,
                dr_pct_after_ft FLOAT,
                tr_pct FLOAT,
                st_pct FLOAT,
                blk_pct FLOAT,
                blk_pct_2p FLOAT,
                blk_pct_3p FLOAT,
                pf_100_poss FLOAT,
                df_100_poss FLOAT,
                per FLOAT,
                off_win_share FLOAT,
                def_win_share FLOAT,
                win_share FLOAT,
                win_share_per_40 FLOAT,
                obpm FLOAT,
                dbpm FLOAT,
                bpm FLOAT,
                vorp FLOAT,
                tm_pace_on FLOAT,
                tm_off_rtg_on FLOAT,
                tm_def_rtg_on FLOAT,
                tm_net_rtg_on FLOAT,
                tm_ts_pct_on FLOAT,
                tm_or_pct_on FLOAT,
                tm_to_pct_on FLOAT,
                tm_ft_ratio_on FLOAT,
                opp_ts_pct_on FLOAT,
                opp_or_pct_on FLOAT,
                opp_to_pct_on FLOAT,
                opp_ft_ratio_on FLOAT,
                tm_pace_off FLOAT,
                tm_off_rtg_off FLOAT,
                tm_def_rtg_off FLOAT,
                tm_net_rtg_off FLOAT,
                tm_ts_pct_off FLOAT,
                tm_or_pct_off FLOAT,
                tm_to_pct_off FLOAT,
                tm_ft_ratio_off FLOAT,
                opp_ts_pct_off FLOAT,
                opp_or_pct_off FLOAT,
                opp_to_pct_off FLOAT,
                opp_ft_ratio_off FLOAT,
                tm_pace_net FLOAT,
                tm_off_rtg_net FLOAT,
                tm_def_rtg_net FLOAT,
                tm_net_rtg_net FLOAT,
                tm_ts_pct_net FLOAT,
                tm_or_pct_net FLOAT,
                tm_to_pct_net FLOAT,
                tm_ft_ratio_net FLOAT,
                opp_ts_pct_net FLOAT,
                opp_or_pct_net FLOAT,
                opp_to_pct_net FLOAT,
                opp_ft_ratio_net FLOAT
            )
            """
        ]

        for command in table_commands:
            cur.execute(command)
        print("Tablas creadas en la base de datos avanzadas.")

        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Error al crear las tablas: {e}")
        if conn:
            conn.close()

def clean_and_load_data():
    conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    seasons_to_insert = ["2023-24", "2024-25"]
    for season in seasons_to_insert:
        cur.execute(
            """
            INSERT INTO seasons (season_id, season_name)
            VALUES (%s, %s)
            ON CONFLICT (season_id) DO NOTHING;
            """,
            (season, season)
        )

    for key, file_path in CSV_FILES.items():
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, delimiter=';')
            season_year = '20' + key.split('_')[0] + '-' + key.split('_')[1]

            # Limpiar datos numéricos y reemplazar "-" por NaN
            for col in df.select_dtypes(include='object').columns.difference(['tm_name', 'name', 'role', 'nat']):
                df[col] = df[col].replace("-", None)
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Diferenciar: stats -> NaN=0, atributos -> mantener NaN
            stats_cols = [c for c in df.columns if c not in ['tm_name', 'name', 'role', 'nat', 'height', 'age']]
            df[stats_cols] = df[stats_cols].fillna(0)

            if 'teams' in key:
                # Insertar equipos
                for _, row in df.iterrows():
                    cur.execute(
                        """
                        INSERT INTO teams (tm_name, season_id)
                        VALUES (%s, %s)
                        ON CONFLICT (tm_name) DO NOTHING;
                        """,
                        (row['tm_name'], season_year)
                    )
                
                # Insertar estadísticas de equipos
                for _, row in df.iterrows():
                    stats_columns = [col for col in df.columns if col not in ['tm_name']]
                    stats_values = [row['tm_name'], season_year] + [row[col] for col in stats_columns]
                    placeholders = ', '.join(['%s'] * len(stats_values))
                    
                    cur.execute(
                        f"""
                        INSERT INTO team_stats (tm_name, season_id, {', '.join(stats_columns)})
                        VALUES ({placeholders});
                        """,
                        stats_values
                    )
            
            elif 'players' in key:
                # Filtrar jugadores sin impacto
                if 'gp' in df.columns and 'min' in df.columns:
                    df = df[(df['gp'] > 3) & (df['min'] > 10)]

                # Insertar jugadores
                for _, row in df.iterrows():
                    cur.execute(
                        """
                        INSERT INTO players (name, role, nat, height, age, tm_name, season_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING;
                        """,
                        (row['name'], row['role'], row['nat'], row['height'], row['age'], row['tm_name'], season_year)
                    )
                
                # Insertar estadísticas de jugadores
                for _, row in df.iterrows():
                    stats_columns = [col for col in df.columns if col not in ['name', 'role', 'nat', 'height', 'age', 'tm_name']]
                    stats_values = [row['name'], row['tm_name'], season_year, row['role'], row['nat'], row['height'], row['age']] + [row[col] for col in stats_columns]
                    placeholders = ', '.join(['%s'] * len(stats_values))
                    
                    cur.execute(
                        f"""
                        INSERT INTO player_stats (name, tm_name, season_id, role, nat, height, age, {', '.join(stats_columns)})
                        VALUES ({placeholders});
                        """,
                        stats_values
                    )

        else:
            print(f"Advertencia: El archivo {file_path} no fue encontrado.")

    cur.close()
    conn.close()
    print("Datos cargados exitosamente.")

if __name__ == '__main__':
    create_advanced_database_and_tables()
    clean_and_load_data()