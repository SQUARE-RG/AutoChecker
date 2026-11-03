enum State { StateOk = 0, StateWarning, StateError };

int main()
{
    unsigned int code = StateError; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-11]
    return code;
}
