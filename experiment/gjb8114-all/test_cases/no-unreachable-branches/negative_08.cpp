int classify(int value)
{
    if (value == 3 && value == 4)
    {
        return 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-2]
    }
    else
    {
        return 0;
    }
}

int main()
{
    return classify(5);
}
