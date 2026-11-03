int main()
{
    int s = 1;
    unsigned int u = 3;
    int count = 0;
    for (; s < u; ++count) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-5]
        s += 2;
    }
    return count;
}
