typedef int GlobalInt;

void functionScope()
{
    typedef double OuterLocal;
    struct LocalClass
    {
        typedef long MemberLong;
        OuterLocal outerValue;
        MemberLong memberValue;
    };

    LocalClass obj;
    obj.outerValue = 1.0;
    obj.memberValue = 2;
}

int main()
{
    functionScope();
    return 0;
}
