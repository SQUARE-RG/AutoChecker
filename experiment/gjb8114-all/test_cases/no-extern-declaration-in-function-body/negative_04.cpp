int counter = 0;

int bump()
{
    {
        extern int counter; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-17]
        counter += 1;
    }
    return counter;
}

int main()
{
    return bump();
}
