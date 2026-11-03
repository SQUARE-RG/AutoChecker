bool evaluate(bool a, bool b, bool c, bool d)
{
    return a && b || c || d; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-4]
}

int main()
{
    bool a = true;
    bool b = false;
    bool c = true;
    bool d = false;
    bool result = evaluate(a, b, c, d);
    return result ? 0 : 1;
}
