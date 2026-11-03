unsigned int Vel(unsigned int *pcData);
unsigned int Acc(unsigned int *pcData);

int main(void)
{
    unsigned int dis = 3;
    unsigned int hei;
    hei = Vel(&dis) / 2;
    unsigned int acc = Acc(&dis);
    (void)acc;
    return 0;
}

unsigned int Vel(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = x * x;
    return x;
}

unsigned int Acc(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = 2 * x;
    return x;
}
