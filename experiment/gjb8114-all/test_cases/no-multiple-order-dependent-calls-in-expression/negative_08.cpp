unsigned int Next(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = x + 1;
    return x;
}

int main()
{
    unsigned int state = 0;
    unsigned int values[4] = {0, 0, 0, 0};
    values[Next(&state)] = Next(&state); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-14]
    return static_cast<int>(values[0]);
}
