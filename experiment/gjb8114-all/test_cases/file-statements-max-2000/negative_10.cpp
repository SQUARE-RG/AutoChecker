#define IF10 if (false) {} if (false) {} if (false) {} if (false) {} if (false) {} if (false) {} if (false) {} if (false) {} if (false) {} if (false) {}
#define IF100 IF10 IF10 IF10 IF10 IF10 IF10 IF10 IF10 IF10 IF10
#define IF if (false) {}

void test()
{
    IF100
    IF100
    IF100
    IF100
    IF100
    IF100
    IF100
    IF100
    IF100
    IF10
    IF10
    IF10
    IF10
    IF10
    IF10
    IF10
    IF10
    IF10
    IF
    IF
    IF
    IF
    IF
    IF
    IF
    IF
    IF
    if (false)
    { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-1]
    }
}

int main()
{
}
