elif selection == "KPI":
   df_final_KPI1 = pd.read_csv(chemin_bd + 'resultat/comparaison_FSa.csv')
   comparaison_FSduree =  pd.read_csv(chemin_bd + 'resultat/comparaison_FSa.csv')
   comparaison_FSduree_nv = pd.read_csv(chemin_bd + '/resultat/df_comparaison_FSdures_nv.csv')
#    st.bar_chart(data = df_top5_acteurs_nv, x='primaryName', y='count', color = 'periode', stack="layered", horizontal=True)
   plot = sns.barplot(data = df_comparaison_FSduree_nv, x='durée_moyenne_films', y='durée_moyenne_series')
   # Affichez le graphique dans Streamlit
   st.pyplot(plot.get_figure())