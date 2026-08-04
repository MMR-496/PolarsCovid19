import polars as pl
import plotly.express as px
import time
import polars.selectors as cs
import json


#pl.Config.set_tbl_cols(-1)


def validar(data: pl.LazyFrame, ini : int):
    
    columnas = data.collect_schema().len()
    #data = data.with_row_index()
    
    if columnas == 40:
        print("Puedo limpiar este archivo de 40 columnas")

        #Borramos los registros que cumplan las siguientes condiciones
        #data = data.remove((pl.col('PAIS_NACIONALIDAD') == 'Otro') | (pl.col('PAIS_NACIONALIDAD') == 'SE DESCONOCE') | (pl.col('PAIS_NACIONALIDAD') == 'Zona Neutral') | (pl.col('PAIS_NACIONALIDAD') == '99'))
        data = (data
            .filter(
                (~pl.col('PAIS_NACIONALIDAD').is_in(['Otro','SE DESCONOCE','Zona Neutral','99'])) & (pl.col('EDAD') <= 95) #Eliminamos registros con nacionalidad confusa y edad no muy realista
            )
        )
        #Total de infectados
        output3 = (data
         .with_columns(
            pl.when(pl.col('CLASIFICACION_FINAL').is_in([1,2,3]))
            .then(pl.lit(1))
            .otherwise(pl.lit(0))
            .alias('INFECTADOS')
            )
        
        .group_by(pl.col('INFECTADOS'))
        .len("Total")
        #.collect()

        )
        #Infectados separados por sexo
        output4 = (data
         .with_columns(
             pl.when((pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('SEXO') == 1))
                 .then(pl.lit('Mujer infectada'))
             
            .when((pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('SEXO') == 2))
                 .then(pl.lit('Hombre infectado'))

            .when((pl.col('CLASIFICACION_FINAL').is_in([4,5,6,7])) & (pl.col('SEXO') == 1))
                 .then(pl.lit('Mujer NO infectada'))

            .when((pl.col('CLASIFICACION_FINAL').is_in([4,5,6,7])) & (pl.col('SEXO') == 2))
                 .then(pl.lit('Hombre NO infectado'))
            
            .otherwise(pl.lit('Otro'))
            .alias('SEPARACION P/SEXO')
             )
        .group_by(pl.col('SEPARACION P/SEXO'))
            .len('CANTIDAD')
            .sort('SEPARACION P/SEXO')
         )
         
         #eta vaina ya jala :D
        #Promedio de separaciones por sexo
        output5 = (data
          .with_columns(
             pl.when((pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('SEXO') == 1))
                 .then(pl.lit('XX1'))
             
            .when((pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('SEXO') == 2))
                 .then(pl.lit('XY1'))

            .when((pl.col('CLASIFICACION_FINAL').is_in([4,5,6,7])) & (pl.col('SEXO') == 1))
                 .then(pl.lit('XX0'))

            .when((pl.col('CLASIFICACION_FINAL').is_in([4,5,6,7])) & (pl.col('SEXO') == 2))
                 .then(pl.lit('XY0'))
            
            .otherwise(pl.lit('Otro'))
            .alias('SEXOSEP')
             )
            .select(pl.col('SEXOSEP'), pl.col('EDAD'))
                .group_by(pl.col('SEXOSEP')).mean()
            
         )
        #---
        output6 = (data
                  .select(
                      pl.col('ENTIDAD_RES'), pl.col('CLASIFICACION_FINAL')
                         ) 
                  .filter(
                      pl.col('CLASIFICACION_FINAL').is_in([1,2,3])
                  )
                  .group_by('ENTIDAD_RES')
                  .len()
                  .sort('len', descending=True)
                  .head(10)

                  )
        #Combinaciones
        output7 = (
            data
            .with_columns(
                pl.when(
                    (pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('RESULTADO_LAB') == 1) & (pl.col('RESULTADO_ANTIGENO') == 1) & (pl.col('FECHA_DEF') == '9999-99-99')
                )
                    .then(pl.lit('Lab y Antigeno, vivo'))
                    

                .when(
                    (pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('RESULTADO_LAB') == 1) & (pl.col('RESULTADO_ANTIGENO') == 1) & (pl.col('FECHA_DEF') != '9999-99-99')
                )
                    .then(pl.lit('Lab y Antigeno, fallecido'))
                    

                .when(
                    (pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('RESULTADO_LAB') == 1) & (pl.col('RESULTADO_ANTIGENO') != 1) & (pl.col('FECHA_DEF') == '9999-99-99')
                )
                    .then(pl.lit('Lab, vivo'))

                 .when(
                    (pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('RESULTADO_LAB') == 1) & (pl.col('RESULTADO_ANTIGENO') != 1) & (pl.col('FECHA_DEF') != '9999-99-99')
                )
                    .then(pl.lit('Lab, fallecido'))

                 .when(
                    (pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('RESULTADO_LAB') != 1) & (pl.col('RESULTADO_ANTIGENO') == 1) & (pl.col('FECHA_DEF') == '9999-99-99')
                )
                    .then(pl.lit('Antigeno, vivo'))

                  .when(
                    (pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('RESULTADO_LAB') != 1) & (pl.col('RESULTADO_ANTIGENO') == 1) & (pl.col('FECHA_DEF') != '9999-99-99')
                )
                    .then(pl.lit('Antigeno, fallecido'))
                 
                 .when(
                    (pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('RESULTADO_LAB') != 1) & (pl.col('RESULTADO_ANTIGENO') != 1) & (pl.col('FECHA_DEF') == '9999-99-99')
                )
                    .then(pl.lit('No lab ni antigeno, vivo'))
                
                .when(
                    (pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('RESULTADO_LAB') != 1) & (pl.col('RESULTADO_ANTIGENO') != 1) & (pl.col('FECHA_DEF') != '9999-99-99')
                )
                    .then(pl.lit('No lab ni antigeno, fallecido'))

                .when(
                    (pl.col('CLASIFICACION_FINAL').is_in([4,5,6,7])) & (pl.col('FECHA_DEF') != '9999-99-99')
                )
                    .then(pl.lit('No infectado, fallecido'))

                
                .when(
                    (pl.col('CLASIFICACION_FINAL').is_in([4,5,6,7])) & (pl.col('FECHA_DEF') == '9999-99-99')
                )
                    .then(pl.lit('No infectado, vivo'))


                    .otherwise(pl.lit('Otros'))
                .alias('Tipo')
                
            )

            .group_by(pl.col('Tipo'))
            .len('Total')
            .sort('Tipo')
            #.sort('len', descending=True)
            
        )
        
        output3, output4, output5, output6, output7 = pl.collect_all([
            output3,
            output4,
            output5,
            output6,
            output7
        ])

        
        #---------------------------------------------
        #VISUALIZACION DE DATOS
        #---------------------------------------------
        #------Pie de combinaciones
        fig = px.pie(
            output7,
            values='Total',
            names='Tipo',
            title='Distribución por diágnostico',
            color='Tipo',
            color_discrete_sequence=px.colors.sequential.Bluyl


        )

        fig.update_traces(textposition='outside', textinfo='percent+label', textfont_size=15)
        fig.show()
        #------Barras de sexos
        fig = px.bar(
            output4,
            x='SEPARACION P/SEXO',
            y='CANTIDAD', 
            color= 'SEPARACION P/SEXO',
            color_discrete_map={
                'Hombre infectado': "#d85c58",
                'Mujer infectada': "#a83a37",
                'Hombre NO infectado': "#1985af",
                'Mujer NO infectada': "#6babcf"
            },
               labels={
                'SEPARACION P/SEXO': 'Grupo',   # así se va a ver en vez de "SEPARACION P/SEXO"
                'CANTIDAD': 'N. Personas'
            },
            template='simple_white',
            width=600)
        fig.show()
        # #------Pie de sexos
        # fig = px.pie(
        #     output4,
        #     values='CANTIDAD',
        #     names='SEPARACION P/SEXO',
        #     title='Distribución por sexo',
        #     color='SEPARACION P/SEXO',
        #     labels={
        #         'SEPARACION P/SEXO': 'Grupo',   # así se va a ver en vez de "SEPARACION P/SEXO"
        #         'CANTIDAD': 'N. Personas'
        #     },
        #     color_discrete_map={
        #         'Hombre infectado': "#6d1e87",
        #         'Mujer infectada': "#c0120c",
        #         'Hombre NO infectado': "#5f5dd1",
        #         'Mujer NO infectada': "#d54597"
        #     },


        # )

        # fig.update_traces(textposition='outside', textinfo='percent+label', textfont_size=15)
        # fig.show()

        # #------Barra de combinaciones
        # fig = px.bar(
        #     output7,
        #     x='Tipo',
        #     y='Total', 
        #     color= 'Tipo',
        #     color_discrete_map={
        #         'Antigeno, fallecido': "#c03e0b",
        #         'Antigeno, vivo': "#38ccf1",
        #         'Lab y Antigeno, fallecido': "#8a4848",
        #         'Lab y Antigeno, vivo': "#d38fe0",
        #         'Lab, fallecido': "#aa400e",
        #         'Lab, vivo':"#99e9e2",
        #         'No infectado, fallecido':"#e01919",
        #         'No infectado, vivo:':"#4bd84b",
        #         'No lab ni antigeno, fallecido':"#5d0b6d",
        #         'No lab ni antigeno, vivo':"#0f93c7"
        #     },
        #     template='simple_white',
        #     width=600)
        # fig.show()

        
        #---------------------------------------------
        #---------------------------------------------
        print('Tipo')
        print(output7)
        print('Total infectados')
        print(output3)
        print('Infectados separados por sexo')
        print(output4)
        print('Promedio de edad separado por sexo e infeccion')
        print(output5)
        print('Debe haber combinado infectados con su estado de residencia nada mas')
        print(output6)
        #print('Nacionalidades')
        #print(output)
        #output.write_csv("despues.txt", separator=",")
        fin = time.time_ns()
        print("Duración del procesamiento: ",(fin-ini)/1e9," segundos")


        #---------------------------------------------
        #---------------------------------------------
        #---------------------------------------------
        #---------------------------------------------
        #---------------------------------------------
        #---------------------------------------------

    elif columnas == 42:
        print("Puedo limpiar este archivo de 42 columnas")
        #Se limṕia el dataset
        data = (data
            .filter(
                (~pl.col('PAIS_NACIONALIDAD').is_in(['Otro','SE DESCONOCE','Zona Neutral','99'])) & (pl.col('EDAD') <= 95) #Eliminamos registros con nacionalidad confusa y edad no muy realista
            )
        )

        #Total de infectados
        output3 = (data
         .with_columns(
            pl.when(pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3]))
            .then(pl.lit(1))
            .otherwise(pl.lit(0))
            .alias('INFECTADOS')
            )
        
        .group_by(pl.col('INFECTADOS'))
        .len("Total")
        )

        #Separacion por sexos
        output4 = (data
         .with_columns(
             pl.when((pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('SEXO') == 1))
                 .then(pl.lit('Mujer infectada'))
             
            .when((pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('SEXO') == 2))
                 .then(pl.lit('Hombre infectado'))

            .when((pl.col('CLASIFICACION_FINAL_COVID').is_in([4,5,6,7])) & (pl.col('SEXO') == 1))
                 .then(pl.lit('Mujer NO infectada'))

            .when((pl.col('CLASIFICACION_FINAL_COVID').is_in([4,5,6,7])) & (pl.col('SEXO') == 2))
                 .then(pl.lit('Hombre NO infectado'))
            
            .otherwise(pl.lit('Otro'))
            .alias('SEPARACION P/SEXO')
             )
        .group_by(pl.col('SEPARACION P/SEXO'))
            .len('CANTIDAD')
            .sort('SEPARACION P/SEXO')
         )
         
        #Separación por sexo e infección, promedio de edad
        output5 = (data
          .with_columns(
             pl.when((pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('SEXO') == 1))
                 .then(pl.lit('XX1'))
             
            .when((pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('SEXO') == 2))
                 .then(pl.lit('XY1'))

            .when((pl.col('CLASIFICACION_FINAL_COVID').is_in([4,5,6,7])) & (pl.col('SEXO') == 1))
                 .then(pl.lit('XX0'))

            .when((pl.col('CLASIFICACION_FINAL_COVID').is_in([4,5,6,7])) & (pl.col('SEXO') == 2))
                 .then(pl.lit('XY0'))
            
            .otherwise(pl.lit('Otro'))
            .alias('SEXOSEP')
             )
            .select(pl.col('SEXOSEP'), pl.col('EDAD'))
                .group_by(pl.col('SEXOSEP')).mean()
                .sort('SEXOSEP')
            
            
         )

        #Combinaciones
        output7 = (
            data
            .with_columns(
                pl.when(
                    (pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('RESULTADO_PCR') == 34) & (pl.col('RESULTADO_ANTIGENO') == 1) & (pl.col('FECHA_DEF') == '9999-99-99')
                )
                    .then(pl.lit('Lab y Antigeno, vivo'))
                    

                .when(
                    (pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('RESULTADO_PCR') == 34) & (pl.col('RESULTADO_ANTIGENO') == 1) & (pl.col('FECHA_DEF') != '9999-99-99')
                )
                    .then(pl.lit('Lab y Antigeno, fallecido'))
                    

                .when(
                    (pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('RESULTADO_PCR') == 34) & (pl.col('RESULTADO_ANTIGENO') != 1) & (pl.col('FECHA_DEF') == '9999-99-99')
                )
                    .then(pl.lit('Lab, vivo'))

                 .when(
                    (pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('RESULTADO_PCR') == 34) & (pl.col('RESULTADO_ANTIGENO') != 1) & (pl.col('FECHA_DEF') != '9999-99-99')
                )
                    .then(pl.lit('Lab, fallecido'))

                 .when(
                    (pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('RESULTADO_PCR') != 34) & (pl.col('RESULTADO_ANTIGENO') == 1) & (pl.col('FECHA_DEF') == '9999-99-99')
                )
                    .then(pl.lit('Antigeno, vivo'))

                  .when(
                    (pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('RESULTADO_PCR') != 34) & (pl.col('RESULTADO_ANTIGENO') == 1) & (pl.col('FECHA_DEF') != '9999-99-99')
                )
                    .then(pl.lit('Antigeno, fallecido'))
                 
                 .when(
                    (pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('RESULTADO_PCR') != 34) & (pl.col('RESULTADO_ANTIGENO') != 1) & (pl.col('FECHA_DEF') == '9999-99-99')
                )
                    .then(pl.lit('No lab ni antigeno, vivo'))
                
                .when(
                    (pl.col('CLASIFICACION_FINAL_COVID').is_in([1,2,3])) & (pl.col('RESULTADO_PCR') != 34) & (pl.col('RESULTADO_ANTIGENO') != 1) & (pl.col('FECHA_DEF') != '9999-99-99')
                )
                    .then(pl.lit('No lab ni antigeno, fallecido'))

                .when(
                    (pl.col('CLASIFICACION_FINAL_COVID').is_in([4,5,6,7])) & (pl.col('FECHA_DEF') != '9999-99-99')
                )
                    .then(pl.lit('No infectado, fallecido'))

                
                .when(
                    (pl.col('CLASIFICACION_FINAL_COVID').is_in([4,5,6,7])) & (pl.col('FECHA_DEF') == '9999-99-99')
                )
                    .then(pl.lit('No infectado, vivo'))


                    .otherwise(pl.lit('Otros'))
                .alias('Tipo')
                
            )

            .group_by(pl.col('Tipo'))
            .len('Total')
            .sort('Tipo')
            #.sort('len', descending=True)
            
        )
        
        output7, output3, output4, output5 = pl.collect_all([
            output7,
            output3,
            output4,
            output5
        ])
        print('Total de infectados')
        print(output3)
        print('Separacion por sexos')
        print(output4)
        print('Promedio de edad, dividido por sexo e infeccion')
        print(output5)
        print('Combinaciones')
        print(output7)

        #---------------------------------------------
        #---------------------------------------------
        #---------------------------------------------
        #VISUALIZACION DE DATOS
        #---------------------------------------------
        #---------------------------------------------
        #---------------------------------------------
        #------Pie de combinaciones
        fig = px.pie(
            output7,
            values='Total',
            names='Tipo',
            title='Distribución por diágnostico',
            color='Tipo',
            color_discrete_sequence=px.colors.sequential.Bluyl


        )

        fig.update_traces(textposition='outside', textinfo='percent+label', textfont_size=15)
        fig.show()
        #------Barras de sexos
        fig = px.bar(
            output4,
            x='SEPARACION P/SEXO',
            y='CANTIDAD', 
            color= 'SEPARACION P/SEXO',
            color_discrete_map={
                'Hombre infectado': "#d85c58",
                'Mujer infectada': "#a83a37",
                'Hombre NO infectado': "#1985af",
                'Mujer NO infectada': "#6babcf"
            },
               labels={
                'SEPARACION P/SEXO': 'Grupo',   # así se va a ver en vez de "SEPARACION P/SEXO"
                'CANTIDAD': 'N. Personas'
            },
            template='simple_white',
            width=600)
        fig.show()
        # #------Pie de sexos
        # fig = px.pie(
        #     output4,
        #     values='CANTIDAD',
        #     names='SEPARACION P/SEXO',
        #     title='Distribución por sexo',
        #     color='SEPARACION P/SEXO',
        #     labels={
        #         'SEPARACION P/SEXO': 'Grupo',   # así se va a ver en vez de "SEPARACION P/SEXO"
        #         'CANTIDAD': 'N. Personas'
        #     },
        #     color_discrete_map={
        #         'Hombre infectado': "#6d1e87",
        #         'Mujer infectada': "#c0120c",
        #         'Hombre NO infectado': "#5f5dd1",
        #         'Mujer NO infectada': "#d54597"
        #     },


        # )

        # fig.update_traces(textposition='outside', textinfo='percent+label', textfont_size=15)
        # fig.show()

        # #------Barra de combinaciones
        # fig = px.bar(
        #     output7,
        #     x='Tipo',
        #     y='Total', 
        #     color= 'Tipo',
        #     color_discrete_map={
        #         'Antigeno, fallecido': "#c03e0b",
        #         'Antigeno, vivo': "#38ccf1",
        #         'Lab y Antigeno, fallecido': "#8a4848",
        #         'Lab y Antigeno, vivo': "#d38fe0",
        #         'Lab, fallecido': "#aa400e",
        #         'Lab, vivo':"#99e9e2",
        #         'No infectado, fallecido':"#e01919",
        #         'No infectado, vivo:':"#4bd84b",
        #         'No lab ni antigeno, fallecido':"#5d0b6d",
        #         'No lab ni antigeno, vivo':"#0f93c7"
        #     },
        #     template='simple_white',
        #     width=600)
        # fig.show()

        



        #output.write_csv("contabilizacion.txt", separator=",")
        fin = time.time_ns()
        print("Duración del procesamiento: ",(fin-ini)/1e9," segundos")
anio = int(input("Elige el año a procesar (2020-2025): "))
if anio in range(2020, 2026):
    ini = time.time_ns()
    print("Iniciando procesamiento")
    data = pl.scan_csv(
        f'COVID19MEXICO{anio}.csv',
        schema_overrides={
            "PAIS_ORIGEN": pl.String
        }
    )
    validar(data, ini)
else: 
    print("No es una opción")


#Esto es de todos los años, así que no importa que opción se escoja, siempre se rendizará la figura
df = pl.DataFrame({
    "SEXOSEP": [
        "Hombre Infectado","Hombre Infectado","Hombre Infectado","Hombre Infectado","Hombre Infectado","Hombre Infectado",
        "Hombre NO Infectado","Hombre NO Infectado","Hombre NO Infectado","Hombre NO Infectado","Hombre NO Infectado","Hombre NO Infectado",
        "Mujer Infectada","Mujer Infectada","Mujer Infectada","Mujer Infectada","Mujer Infectada","Mujer Infectada",
        "Mujer NO Infectada","Mujer NO Infectada","Mujer NO Infectada","Mujer NO Infectada","Mujer NO Infectada","Mujer NO Infectada",
    ],
    "ANIO": [
        2020,2021,2022,2023,2024,2025,
        2020,2021,2022,2023,2024,2025,
        2020,2021,2022,2023,2024,2025,
        2020,2021,2022,2023,2024,2025,
    ],
    "EDAD_PROMEDIO": [
        43.328905,39.186322,38.891379,42.432731,43.485141,41.578341,
        39.297105,37.452445,36.811603,37.183085,37.681269,36.912470,
        39.116872,39.073614,37.954026,40.600500,44.598175,39.578087,
        39.116872,36.364410,35.155579,34.449414,34.196811,32.825702,
    ]
})

fig = px.line(df, 
              x= 'ANIO', 
              y ='EDAD_PROMEDIO', 
              color ='SEXOSEP', 
              markers=True, 
              title='Promedio de edad por año',
              labels={'EDAD_PROMEDIO':'Edad Promedio', 
                      'ANIO': 'Año',
                      'SEXOSEP': 'Grupo'},
               color_discrete_map={
                    'Hombre infectado': "#d85c58",
                    'Mujer infectada': "#a83a37",
                    'Hombre NO infectado': "#1985af",
                    'Mujer NO infectada': "#6babcf"
            }
              )
fig.show()

#Distribución de infectados y no infectados conforme los años

df2 = pl.DataFrame({
    "INFECCION": [
        "No infectado", "Infectado",
        "No infectado", "Infectado",
        "No infectado", "Infectado",
        "No infectado", "Infectado",
        "No infectado", "Infectado",
        "No infectado", "Infectado",
                ],
    "ANIO": [
        2020, 2020,
        2021, 2021,
        2022, 2022,
        2023, 2023,
        2024, 2024,
        2025, 2025
            ],
    "INFECTADOS": [
        2303017, 1561924,
        6295719, 2524894,
        3253221, 3193199,
        792900, 427792,
        163103, 14078,
        149452, 7215
                  ]
})

fig = px.line(df2, 
              x= 'ANIO', 
              y ='INFECTADOS', 
              color ='INFECCION', 
              markers=True, 
              title='Infectados por año',
              labels={'INFECTADOS':'Personas', 
                      'ANIO': 'Año',
                      'INFECCION': 'Grupo'},
               color_discrete_map={
                    'No infectado': "#3bda3b",
                    'Infectado': "#ac2722"
            }
              )
fig.show()



def leer(anio):
        return pl.scan_csv(
        f'COVID19MEXICO{anio}.csv',
        schema_overrides={
            "PAIS_ORIGEN": pl.String
        }
    )    

data20 = leer(2020).with_columns(pl.lit(2020).alias("ANIO")).filter((pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('NACIONALIDAD') == 1 ) & (pl.col('EDAD') <= 95)).select(pl.col('ENTIDAD_RES'), pl.col('CLASIFICACION_FINAL'), pl.col('ANIO'))
data21 = leer(2021).with_columns(pl.lit(2021).alias("ANIO")).filter((pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('NACIONALIDAD') == 1 ) & (pl.col('EDAD') <= 95)).select(pl.col('ENTIDAD_RES'), pl.col('CLASIFICACION_FINAL'), pl.col('ANIO'))
data22 = leer(2022).with_columns(pl.lit(2022).alias("ANIO")).filter((pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('NACIONALIDAD') == 1 ) & (pl.col('EDAD') <= 95)).select(pl.col('ENTIDAD_RES'), pl.col('CLASIFICACION_FINAL'), pl.col('ANIO'))
data23 = leer(2023).with_columns(pl.lit(2023).alias("ANIO")).filter((pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('NACIONALIDAD') == 1 ) & (pl.col('EDAD') <= 95)).select(pl.col('ENTIDAD_RES'), pl.col('CLASIFICACION_FINAL'), pl.col('ANIO'))
data24 = leer(2024).with_columns(pl.lit(2024).alias("ANIO"), pl.col('CLASIFICACION_FINAL_COVID').alias('CLASIFICACION_FINAL')).filter((pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('NACIONALIDAD') == 1 ) & (pl.col('EDAD') <= 95)).select(pl.col('ENTIDAD_RES'), pl.col('CLASIFICACION_FINAL'), pl.col('ANIO'))
data25 = leer(2025).with_columns(pl.lit(2025).alias("ANIO"), pl.col('CLASIFICACION_FINAL_COVID').alias('CLASIFICACION_FINAL')).filter((pl.col('CLASIFICACION_FINAL').is_in([1,2,3])) & (pl.col('NACIONALIDAD') == 1 ) & (pl.col('EDAD') <= 95)).select(pl.col('ENTIDAD_RES'), pl.col('CLASIFICACION_FINAL'), pl.col('ANIO'))

df = (
    pl.concat([data20, data21, data22, data23, data24, data25])
    .group_by(["ANIO", "ENTIDAD_RES"])
    .len(name="PERSONAS")
    .sort(["ANIO", "ENTIDAD_RES"])
    .collect()
)

mexico_states = json.load((open('mx.json', 'r')))

# El GeoJSON tiene códigos (ID) distintos a nuestro dataframe, 
# por lo tanto necesitamos reemplazarlos en nuestro df
# para que coincidan con los del GeoJSON
# para mayor legibilidad en el mapa, utilizamos el nombre del estado
# con el diccionario nso apoyaremso para reemplazar los valores de nuestro df
estados = {
        1 : 'Aguascalientes',
        2 : 'Baja California',
        3 : 'Baja California Sur',
        4 : 'Campeche',
        5 : 'Coahuila',
        6 : 'Colima',
        7 : 'Chiapas',
        8 : 'Chihuahua',
        9 : 'Ciudad de Mexico',
        10 : 'Durango',
        11 : 'Guanajuato',
        12 : 'Guerrero',
        13 : 'Hidalgo',
        14 : 'Jalisco',
        15 : 'Mexico',
        16 : 'Michoacan',
        17 : 'Morelos',
        18 : 'Nayarit',
        19 : 'Nuevo Leon',
        20 : 'Oaxaca',
        21 : 'Puebla',
        22 : 'Queretaro',
        23 : 'Quintana Roo',
        24 : 'San Luis Potosi',
        25 : 'Sinaloa',
        26 : 'Sonora',
        27 : 'Tabasco',
        28 : 'Tamaulipas',
        29 : 'Tlaxcala',
        30 : 'Veracruz',
        31 : 'Yucatan',
        32 : 'Zacatecas'
}

df = (df
        .with_columns(pl.col('ENTIDAD_RES').replace_strict(estados, return_dtype=pl.String).alias('ENTIDAD_RES'))
)

fig = px.choropleth(df, 
                    locations='ENTIDAD_RES', 
                    geojson=mexico_states, 
                    featureidkey='properties.name', #Por default es id, pero en este caso tomamos el nombre
                    color='PERSONAS', 
                    animation_frame='ANIO', #Nos mostrará una animación basada en el tiempo
                    title = 'Infectados mexicanos con el tiempo',
                    labels= {
                            'ENTIDAD_RES' : 'Estado',
                            'PERSONAS' : 'Personas',
                            'ANIO' : 'Año'
                    },
                    #color_continuous_scale="Reds",
                    range_color=(0, 800_000),
                    )
fig.show()
