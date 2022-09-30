#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Range
from geometry_msgs.msg import Twist

# Definitions des dictionnaires qui vont me permettre d enregistrer les 
# messages des differents capteurs, et l etat dans lequel se trouve le
# robot. Ces dictionnaires sont definis en tant que variables globales
# pour etre utilises dans les differentes fonctions du script.
dict_regions = {
    'av_droit': 0,
    'av': 0,
    'av_gauche': 0,
}
dict_etat = {
    0: 'cherche le mur',
    1: 'evite le mur',
    2: 'suit le mur',
}
etat_courrant = 0
publisher = None

# Definis les fonctions qui recoivent les messages des capteurs.
def capteur_avantgauche(msg):
    global dict_regions  
    dict_regions['av_gauche'] = msg.range
    action()
def capteur_avantdroit(msg):
    global dict_regions  
    dict_regions['av_droit'] = msg.range
    action()
def capteur_avant(msg):
    global dict_regions  
    dict_regions['av'] = msg.range
    action()
    
# Definition d une fonction qui permet de changer l etat du robot en 
# fonction d une entree en parametre, elle affiche en plus l etat courant.  
def changer_etat(etat):
    global etat_courrant, dict_etat

    if etat is not etat_courrant:
        print('Mur suiveur - [%s] - %s' % (etat_courrant, dict_etat[etat]))
        etat_courrant = etat

# Definition de la fonction principale du script, celle qui va prendre une
# action entre les 3 definis precedemment, selon ce que les capteurs ont renvoyes.
def action():
    global dict_regions
    regions = dict_regions

    msg = Twist()
    linear_x = 0
    angular_z = 0
    etat_desc = ''
    distance_av = 0.5
    distance = 0.5

    print(regions)
    
    if regions['av'] > distance_av and regions['av_gauche'] > distance and regions['av_droit'] > distance :
        etat_desc = '1 - rien detecter => etat cherche mur'
        changer_etat(0)

    elif regions['av'] < distance_av and regions['av_gauche'] > distance and regions['av_droit'] > distance :
        etat_desc = '2 - probleme_avant => etat evite mur'
        changer_etat(1)

    elif regions['av'] > distance_av and regions['av_gauche'] < distance and regions['av_droit'] > distance :
        etat_desc = '3 - probleme_avant_gauche=> etat suit mur'
        changer_etat(2)

    elif regions['av'] > distance_av and regions['av_gauche'] < distance and regions['av_droit'] > distance :
        etat_desc = '4 - probleme _avant_gauche => etat cherche mur'
        changer_etat(0)

    elif regions['av'] < distance_av and regions['av_gauche'] > distance and regions['av_droit'] < distance :
        etat_desc = '5 - probleme _avant & probleme _avant_droit => etat evite mur'
        changer_etat(1)
    
    elif regions['av'] < distance_av and regions['av_gauche'] < distance and regions['av_droit'] > distance :
        etat_desc = '6 - probleme _avant & probleme _avant_gauche => etat evite mur'
        changer_etat(1)

    
    elif regions['av'] < distance_av and regions['av_gauche'] < distance and regions['av_droit'] < distance :
        etat_desc = '7 - probleme _avant & probleme _avant_gauche & probleme _avant_droit => etat evite mur'
        changer_etat(1)
    
    elif regions['av'] > distance_av and regions['av_gauche'] < distance and regions['av_droit'] < distance :
        etat_desc = '8 - probleme _avant_gauche & probleme _avant_droit => etat cherche mur'
        changer_etat(0)

    else:
        etat_desc ='etat inconnu'
    
    print(etat_desc)
    
# Definition des fonctions qui realisent les differentes actions
def cherche_mur():
    msg = Twist()
    msg.linear.x = 0.3
    msg.angular.z = -0.6
    return msg
def evite_mur():
    msg = Twist()
    msg.angular.z = 1
    return msg
def suivre_mur():
    msg = Twist()
    msg.linear.x = 0.2
    return msg

# Fonction main qui lancer les actions avec le publisher et les differents 
# etats du robot.
def main():
    global publisher_
    rospy.init_node('solver_labyrinthe')

    publisher=rospy.Publisher('/mobile_robot/cmd_vel',Twist,queue_size=1)
    rospy.Subscriber('/mobile_robot/sonar_right_front',Range,capteur_avantdroit)
    rospy.Subscriber('/mobile_robot/sonar_left_front',Range,capteur_avantgauche)
    rospy.Subscriber('/mobile_robot/sonar_front',Range,capteur_avant)

    rate = rospy.Rate(20)

    while not rospy.is_shutdown():
        msg = Twist()
        if etat_courrant == 0:
            msg = cherche_mur()

        elif etat_courrant == 1:
            msg = evite_mur()

        elif etat_courrant == 2:
            msg = suivre_mur()


        publisher.publish(msg)
        rate.sleep()


main()

