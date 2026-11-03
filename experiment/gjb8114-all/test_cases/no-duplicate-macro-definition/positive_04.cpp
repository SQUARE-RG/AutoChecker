#define SCALE(x) ((x) * 2)

int double_value(int v)
{
    return SCALE(v);
}

#undef SCALE
#define SCALE(x) ((x) * 3)

int main()
{
    int result = double_value(4) + SCALE(2);
    (void)result;
    return 0;
}
