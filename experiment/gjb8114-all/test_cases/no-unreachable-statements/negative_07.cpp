int compute(int input)
{
    int result = input;
    goto finish;
    result = result + 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-1]
finish:
    return result;
}

int main(int argc, char** argv)
{
    return compute(argc);
}
