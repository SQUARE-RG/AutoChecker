enum { A_Level = 0, B_Level, C_Level, D_Level } eLevel; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-8]

int main()
{
    eLevel = B_Level;
    return 0;
}
