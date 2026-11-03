#include <iostream>

struct A
{
    A() : a(0) {}
    void SetA(int va) { a = va; }
private:
    int a;
};

struct B1 : virtual A
{
    B1() : A(), b1(0) {}
    void SetB1(int vb)
    {
        b1 = vb;
        SetA(b1 + 1);
    }
private:
    int b1;
};

struct B2 : public virtual A
{
    B2() : A(), b2(0) {}
    void SetB2(int vb)
    {
        b2 = vb;
        SetA(b2 + 2);
    }
private:
    int b2;
};

struct D : B1, B2
{
    D() : B1(), B2(), d(0) {}
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
