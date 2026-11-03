static int make_initial() { return 42; }

int global_value = make_initial();

int main()
{
    return global_value - 42;
}
