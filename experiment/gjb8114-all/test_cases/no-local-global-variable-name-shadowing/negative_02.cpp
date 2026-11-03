int flag = 0;
int main()
{
    if (flag == 0) {
        int flag = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-1]
        return flag;
    }
    return flag;
}
