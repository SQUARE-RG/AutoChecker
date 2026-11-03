#define DECLARE_LOCAL_CLASS(name, member) class name { public: int member; }

int main()
{
    DECLARE_LOCAL_CLASS(Holder, count);
    Holder holder;
    holder.count = 5;
    return holder.count == 5 ? 0 : 1;
}
