

/* 1. Configurazione */

epsilon(0.1).

name_game("FrozenLake-v1").
//name_game("CliffWalking-v0").
//name_game("Taxi-v3").

render_mode("human").
//render_mode("ansi").

max_episode_steps(100).
episode_count(500).

file("prova_lake.pkl").
//file("prova_walk.pkl").
//file("prova_taxi.pkl").

/* 2. Start */
+start <-
    .print("[BDI] Agent started, waiting for newState...");
    !init_env;
    !init_qtable;
    !run_episodes.

/* 3. Q table initialization */
+!init_qtable : file(F) <-
    .print("[BDI] Initializing Q-table");
    executeAction(load_qtable, F).

+qtable(S,A,R)[source(percept)]<-
    +qtable(S,A,R)[source(self)];
    -qtable(S,A,R)[source(percept)].

/* 4. environment initialization */
+!init_env : name_game(Name) & render_mode(Mode) & max_episode_steps(Step) <-
    .print("[BDI] Initializing game: ", Name, ", mode: ", Mode, ", step: ", Step);
    executeAction(new_game, Name, Mode, Step).


/* 5. Episode loop */
+!run_episodes : episode_count(N) & N > 0 & file(F) <-
    -episode_count(N);
    N1 = N - 1;
    +episode_count(N1);
    .print("[BDI] Starting episode ", (N - N1), " of ", N + 1);
    !start_episode.

+!run_episodes : episode_count(0) <-
    .print("[BDI] All episodes completed").


/* 6. start single episode */
+!start_episode <-

    -myState(_);
    +myState(0);          /* Placeholder, overwritten by newState after reset_env returns */
    -myAction(_);
    +myAction(none);
    .print("[BDI] Episode reset, waiting for first newState...");
    executeAction(reset_env).

/* 7. Receive environmental feedback and trigger learning and decision making */
+newState(S, Reward, Done)[source(percept)] <-

    .print("↪ newState: state=", S, ", reward=", Reward, ", done=", Done);

    -myState(_);
    +myState(S);

    if (Done) {
        .print("🏁 Episode finished");
        !run_episodes;
    } else {
        !selectAction;
    }.

/* 8. ε-Greedy Decision */
@selectAction
+!selectAction : myState(S) & epsilon(E) <-

    .findall(q(Qv,A,S), qtable(S,A,Qv), L);
    .random(R);
    if (R > E) {
        .max(L, q(_,Act,_));
    } else {
        .shuffle(L, L1);
        .nth(0, L1, q(_,Act,_));
    };
    .print("→ choose action=", Act, " in state=", S);
    -myAction(_);
    +myAction(Act);
    executeAction(step_env, Act).
