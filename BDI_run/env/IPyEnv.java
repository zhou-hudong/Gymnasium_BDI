package app1.env;


/**
 Java interface, which must be implemented on the Python side
 */
public interface IPyEnv {
    void initialize(String envName, String renderMode, String numStep);
    int reset();
    Object[] step(int action);

    int get_Num_States();
    int get_Num_Actions();
}
