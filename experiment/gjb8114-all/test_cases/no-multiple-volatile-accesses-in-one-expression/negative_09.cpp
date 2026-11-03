int main()
{
    volatile unsigned int v = 2;
    unsigned int* p = new unsigned int[v + v]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-13]
    delete[] p;
    return 0;
}
