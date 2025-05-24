# Gymnasium_BDI
Python Gymnasium Q-Learning with BDI agent in java

## Elenco

1. [Rapresentazione progetto](#Rapresentazione_progetto)
2. [Ambiente](#Ambiente)
3. [Run Project](#Run_Project)
4. [Code](#Code)
5. [Configurazione BDI](#Configurazione)
6. [Struttura del progetto](#Struttura_Project)
7. [Note](#Note)

## Rapresentazione_progetto

Il progetto **Gymnasium_BDI** integra un agente BDI (Belief–Desire–Intention) scritto in Java con l’ambiente di simulazione **Gymnasium** di Python, utilizzando **Py4J** come ponte di comunicazione. L’obiettivo è dimostrare come un agente basato su regole (definito in Jason/ASL) possa apprendere politiche ottimali in problemi di rinforzo discreti (ad es. FrozenLake-v1, Taxi-v3) tramite **Q-Learning**.

- **Architettura ibrida**  
  - **Java / Jason**: gestisce la logica BDI, la selezione delle azioni ε-greedy e la gestione delle Belief (Q-table).  
  - **Python / Gymnasium**: fornisce l’ambiente di simulazione (reset, step, render) e le sue dinamiche.  
  - **Py4J**: permette alle due parti di invocarsi a vicenda in modo sincrono e asincrono.

- **Workflow di un episodio**  
  1. **reset_env** (Java → Python) - *inizializzazione ambiente*
  2. Python restituisce 'newState(state, reward, done)'  
  3. L'agente BDI riceve 'newState(state, reward, done)', aggiorna Q-table (!learn) e seleziona la prossima azione (!selectAction)  
  4. **step_env(action)** invocato su Python - *manda prossimo azione all'ambiente*
  5. Nuovo `newState(...)`, ripetizione finché `done=true` (fine di un episodio)

- **Caratteristiche principali**  
  - Calcolo automatico di `num_states` e `num_actions` direttamente da Gymnasium  
  - Supporto a modalità di rendering `human` (grafico) e `ansi` (testuale - *per velocizzare learning*)  
  - Salvataggio e caricamento della Q-table (`.pkl`) per riprendere o analizzare le sessioni di apprendimento  
  - Configurabile via ASL - *senza modificare parte java e python*: learning rate, discount factor, ε-decay, numero di episodi, numero steps per episodio, ambiente di gioco

Questa soluzione consente di esplorare scenari di apprendimento per rinforzo mantenendo una chiara separazione tra **strategia BDI** e **dinamica ambientale**, facilitando estensioni a nuovi giochi Gymnasium con cambi minimi nella configurazione ASL.  

## Ambiente

## Run_Project

## Code

## Configurazione

## Struttura_Project

## Note

Puoi osservare che in modalità ansi, la velocità di learning non era molto veloce, era perchè ho aggiunto un spleep, per evitare che **py4j** si blocchi il taffico di comunicazione tra **java** e **python**
> **Python**
> def step(self, action: int):
>   ...
>   time.sleep(0.2)
>   ...
