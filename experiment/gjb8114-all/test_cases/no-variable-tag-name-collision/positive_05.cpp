union DATA
{
  int i;
  double d;
};

int main()
{
  union DATA data;
  data.i = 1;
  return data.i;
}
