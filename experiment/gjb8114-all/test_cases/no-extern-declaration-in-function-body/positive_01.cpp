extern int global_value;
int global_value = 0;

extern int compute(int, int);

int compute(int a, int b)
{
    return a + b;
}

int main()
{
    int result = compute(global_value, 2);
    return result;
}
