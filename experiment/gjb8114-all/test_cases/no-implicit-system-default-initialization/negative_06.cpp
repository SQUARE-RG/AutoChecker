int next_id()
{
    thread_local int counter; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-2]
    counter = counter + 1;
    return counter;
}

int main()
{
    return next_id();
}
