unsigned int fun(unsigned int par);

int main()
{
    unsigned int value = fun(1u);
    return static_cast<int>(value);
}

unsigned int fun(unsigned int par)
{
    if (par == 1u)
    {
        return -1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-10]
    }
    return par + 1u;
}
