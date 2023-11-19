def test_minimal():
    from minimal import Process
    from entropic import results
    from entropic.sources import Iteration

    pipeline = Process()
    pipeline.run()

    assert len(results.all) == 1

    result = results.all[0]
    assert isinstance(result, Iteration)
    assert result.dump() == {
        "samples": [
            {
                "data": {
                    "file_path": "tests/mocks/kinematic1.csv",
                    "raw": '{"t":{"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"11":11,"12":12,"13":13,"14":14,"15":15,"16":16,"17":17,"18":18,"19":19,"20":20,"21":21,"22":22,"23":23,"24":24,"25":25,"26":26,"27":27,"28":28,"29":29,"30":30,"31":31,"32":32,"33":33,"34":34,"35":35,"36":36,"37":37,"38":38,"39":39,"40":40,"41":41,"42":42,"43":43,"44":44,"45":45,"46":46,"47":47,"48":48,"49":49,"50":50},"x":{"0":0.0006028877,"1":1.0143270109,"2":2.0896294045,"3":3.0559489106,"4":4.0444816227,"5":5.0438843288,"6":6.0599405931,"7":7.0019784031,"8":8.0035265731,"9":9.0121642051,"10":10.0839387322,"11":11.002677866,"12":12.0640091259,"13":13.0447291764,"14":14.0714535922,"15":15.004979983,"16":16.020919955,"17":17.0485963006,"18":18.0530166209,"19":19.0530802987,"20":20.032198616,"21":21.0751459175,"22":22.081262733,"23":23.0148714869,"24":24.0293782801,"25":25.0571441412,"26":26.0531914166,"27":27.0735883833,"28":28.0191000072,"29":29.0633174225,"30":30.0285413117,"31":31.0321073589,"32":32.0440306168,"33":33.0944812353,"34":34.0894234214,"35":35.0663092116,"36":36.0426617488,"37":37.0243157189,"38":38.0565399412,"39":39.0778950581,"40":40.0528061226,"41":41.0083338064,"42":42.0428209471,"43":43.09541261,"44":44.0018660612,"45":45.0253378502,"46":46.0629996106,"47":47.0773238368,"48":48.0392278996,"49":49.0414334307,"50":50.0693405691}}',
                }
            },
            {
                "data": {
                    "file_path": "tests/mocks/kinematic1.csv",
                    "raw": '{"t":{"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"11":11,"12":12,"13":13,"14":14,"15":15,"16":16,"17":17,"18":18,"19":19,"20":20,"21":21,"22":22,"23":23,"24":24,"25":25,"26":26,"27":27,"28":28,"29":29,"30":30,"31":31,"32":32,"33":33,"34":34,"35":35,"36":36,"37":37,"38":38,"39":39,"40":40,"41":41,"42":42,"43":43,"44":44,"45":45,"46":46,"47":47,"48":48,"49":49,"50":50},"x":{"0":0.0006028877,"1":1.0143270109,"2":2.0896294045,"3":3.0559489106,"4":4.0444816227,"5":5.0438843288,"6":6.0599405931,"7":7.0019784031,"8":8.0035265731,"9":9.0121642051,"10":10.0839387322,"11":11.002677866,"12":12.0640091259,"13":13.0447291764,"14":14.0714535922,"15":15.004979983,"16":16.020919955,"17":17.0485963006,"18":18.0530166209,"19":19.0530802987,"20":20.032198616,"21":21.0751459175,"22":22.081262733,"23":23.0148714869,"24":24.0293782801,"25":25.0571441412,"26":26.0531914166,"27":27.0735883833,"28":28.0191000072,"29":29.0633174225,"30":30.0285413117,"31":31.0321073589,"32":32.0440306168,"33":33.0944812353,"34":34.0894234214,"35":35.0663092116,"36":36.0426617488,"37":37.0243157189,"38":38.0565399412,"39":39.0778950581,"40":40.0528061226,"41":41.0083338064,"42":42.0428209471,"43":43.09541261,"44":44.0018660612,"45":45.0253378502,"46":46.0629996106,"47":47.0773238368,"48":48.0392278996,"49":49.0414334307,"50":50.0693405691}}',
                }
            },
        ],
        "source_path": "tests/mocks/",
    }
