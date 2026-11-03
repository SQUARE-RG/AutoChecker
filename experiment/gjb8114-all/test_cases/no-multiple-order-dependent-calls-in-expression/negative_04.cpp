unsigned int Vel(unsigned int *pcData);
unsigned int Acc(unsigned int *pcData);

int main(void)
{
    unsigned int dis = 3;
    unsigned int hei = 0;
    if (Vel(&dis) < Acc(&dis)) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-14]
    {
        hei = 1;
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
