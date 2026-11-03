int classify(char c)
{
    int result = 0;
    switch (c) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-6]
        case 'a':
            result = 1;
            break;
        case 'b':
            result = 2;
            break;
    }
    return result;
}

int main()
{
    return classify('a');
}
