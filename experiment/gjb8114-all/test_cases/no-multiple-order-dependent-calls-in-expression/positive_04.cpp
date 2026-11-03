unsigned int Vel(unsigned int *pcData);
unsigned int Acc(unsigned int *pcData);

int main(void)
{
    unsigned int dis = 3;
    unsigned int first = Vel(&dis);
    unsigned int second = 0;
    while (first > 0)
    {
        second = Acc(&dis);
        break;
    }
    return (int)second;
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
