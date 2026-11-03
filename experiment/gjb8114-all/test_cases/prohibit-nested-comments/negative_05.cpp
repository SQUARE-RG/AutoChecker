int main()
{
    int values[] = {
        1,
        // CHECK-MESSAGES: :[[@LINE+3]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-6]
        /*
        first element
        /* nested block comment marker
        second element
        */
        2, 3
    };
    return values[0];
}
