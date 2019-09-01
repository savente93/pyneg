?::boolean_True;?::boolean_False.
?::integer_0;?::integer_1;?::integer_2;?::integer_3;?::integer_4;?::integer_5;?::integer_6;?::integer_7;?::integer_8;?::integer_9.
?::'float_0.0';?::'float_0.1';?::'float_0.2';?::'float_0.3';?::'float_0.4';?::'float_0.5';?::'float_0.6';?::'float_0.7';?::'float_0.8';?::'float_0.9'.
boolean_True :- integer_2, 'float_0.1'.
utility(boolean_True,100).
utility(boolean_False,10).
utility(integer_9,100).
utility(integer_3,10).
utility(integer_1,0.1).
utility(integer_4,-10).
utility(integer_5,-100).
utility('float_0.1',1).

