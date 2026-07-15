import polars as pl
import plotly.express as px
import time
import polars.selectors as cs


#pl.Config.set_tbl_cols(-1)


def validar(data: pl.LazyFrame, ini : int):
    
    columnas = data.collect_schema().len()
    #data = data.with_row_index()
    
    if columnas == 40:
        print("Puedo limpiar este archivo de 40 columnas")
        
        edades = (data
         .group_by('EDAD')
         .len()
         .sort('len', descending=True)
         #.collect()
        )
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
        
        output7, output3, output4, output5, edades = pl.collect_all([
            output7,
            output3,
            output4,
            output5, 
            edades
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
        #fig.show()
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
        #fig.show()
        #------Pie de sexos
        fig = px.pie(
            output4,
            values='CANTIDAD',
            names='SEPARACION P/SEXO',
            title='Distribución por sexo',
            color='SEPARACION P/SEXO',
            labels={
                'SEPARACION P/SEXO': 'Grupo',   # así se va a ver en vez de "SEPARACION P/SEXO"
                'CANTIDAD': 'N. Personas'
            },
            color_discrete_map={
                'Hombre infectado': "#6d1e87",
                'Mujer infectada': "#c0120c",
                'Hombre NO infectado': "#5f5dd1",
                'Mujer NO infectada': "#d54597"
            },


        )

        fig.update_traces(textposition='outside', textinfo='percent+label', textfont_size=15)
        #fig.show()

        #------Barra de combinaciones
        fig = px.bar(
            output7,
            x='Tipo',
            y='Total', 
            color= 'Tipo',
            color_discrete_map={
                'Antigeno, fallecido': "#c03e0b",
                'Antigeno, vivo': "#38ccf1",
                'Lab y Antigeno, fallecido': "#8a4848",
                'Lab y Antigeno, vivo': "#d38fe0",
                'Lab, fallecido': "#aa400e",
                'Lab, vivo':"#99e9e2",
                'No infectado, fallecido':"#e01919",
                'No infectado, vivo:':"#4bd84b",
                'No lab ni antigeno, fallecido':"#5d0b6d",
                'No lab ni antigeno, vivo':"#0f93c7"
            },
            template='simple_white',
            width=600)
        #fig.show()

        
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
        print(edades)
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
