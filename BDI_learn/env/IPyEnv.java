package app1.env;


/**
 Interfaccia Java, che deve essere implementata dal lato Python
 */
public interface IPyEnv {
    void initialize(String envName, String renderMode, String numStep);
    int reset();
    Object[] step(int action);

    int get_Num_States();
    int get_Num_Actions();
}
