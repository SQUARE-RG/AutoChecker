unsigned int Vel(unsigned int *pcData);

unsigned int Constant(void)
{
    return 7;
}

int main(void)
{
    unsigned int dis = 3;
    unsigned int hei = Vel(&dis) + Constant();
    return 0;
}

unsigned int Vel(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = x * x;
    return x;
}
