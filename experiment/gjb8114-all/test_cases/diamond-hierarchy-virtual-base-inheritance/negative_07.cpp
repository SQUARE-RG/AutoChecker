#include <iostream>
using namespace std;

class A
{
public:
    A() : a(0) {}
    void SetA(int va) { a = va; }
private:
    int a;
};

class Holder
{
public:
    class B1 : public A // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-3]
    {
    public:
        B1() : A(), b1(0) {}
        void SetB1(int vb) { b1 = vb; SetA(b1 + 1); }
    private:
        int b1;
    };
};

class B2 : public virtual A
{
public:
    B2() : A(), b2(0) {}
    void SetB2(int vb) { b2 = vb; SetA(b2 + 2); }
private:
    int b2;
};

class D : public Holder::B1, public B2
{
public:
    D() : Holder::B1(), B2(), d(0) {}
private:
    int d;
};

int main()
{
    D thed;
    thed.SetB1(1);
    thed.SetB2(2);
    return 0;
}
