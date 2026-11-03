int classify(int code)
{
    switch (code)
    {
        case 0:
            return 10;
        case 1:
            return 20;
        default:
            break;
    }
} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-7]

int main()
{
    return classify(0) == 10 ? 0 : 1;
}
