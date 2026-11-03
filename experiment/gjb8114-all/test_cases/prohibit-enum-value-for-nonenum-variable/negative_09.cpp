enum Mode { modeA = 1, modeB = 2 };

int main()
{
    unsigned int values[3] = { 0, 0, 0 };
    values[0] = modeB; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-11]
    return 0;
}
