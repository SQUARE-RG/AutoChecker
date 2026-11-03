int classify(int code) {
  int result = 0;
  switch (code) {
  case 1:
    result = 1;
    [[fallthrough]];
  case 2:
    result += 2;
    break;
  default:
    result = 3;
  }
  return result;
}
