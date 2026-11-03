unsigned int Vel(unsigned int *pcData);

int main(void)
{
    unsigned int dis = 3;
    unsigned int hei;
    hei = (dis > 5) ? 0u : Vel(&dis);
    return 0;
}

unsigned int Vel(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = x * x;
    return x;
}
