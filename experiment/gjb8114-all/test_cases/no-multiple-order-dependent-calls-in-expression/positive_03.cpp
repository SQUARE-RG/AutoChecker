unsigned int Vel(unsigned int *pcData);
unsigned int Acc(unsigned int *pcData);

int main(void)
{
    unsigned int dis = 3;
    unsigned int hei = 0;
    if (Vel(&dis) > 0)
    {
        hei = Acc(&dis);
    }
    return (int)hei;
}

unsigned int Vel(unsigned int *pcData)
{
    unsigned int x = (*pcData);
    (*pcData) = x * x;
    return x;
}

unsigned int Acc(unsigned int *pcData)
{
    unsigned int x = (*pcData);
    (*pcData) = 2 * x;
    return x;
}
